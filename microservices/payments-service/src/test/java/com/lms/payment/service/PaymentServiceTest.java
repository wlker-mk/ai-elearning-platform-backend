package com.lms.payment.service;

import com.lms.payment.dto.PaymentRequest;
import com.lms.payment.dto.PaymentResponse;
import com.lms.payment.exception.PaymentException;
import com.lms.payment.gateway.PaymentGatewayFactory;
import com.lms.payment.gateway.StripePaymentGateway;
import com.lms.payment.model.entity.Payment;
import com.lms.payment.model.enums.PaymentMethod;
import com.lms.payment.model.enums.PaymentStatus;
import com.lms.payment.repository.PaymentRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {
    
    @Mock
    private PaymentRepository paymentRepository;
    
    @Mock
    private PaymentGatewayFactory gatewayFactory;
    
    @Mock
    private DiscountService discountService;
    
    @Mock
    private StripePaymentGateway stripeGateway;
    
    @InjectMocks
    private PaymentService paymentService;
    
    private PaymentRequest testRequest;
    private Payment testPayment;
    private PaymentResponse testResponse;
    
    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(paymentService, "platformFeePercentage", 10.0);
        
        testRequest = new PaymentRequest();
        testRequest.setStudentId("student-123");
        testRequest.setAmount(new BigDecimal("100.00"));
        testRequest.setCurrency("USD");
        testRequest.setMethod(PaymentMethod.STRIPE);
        testRequest.setDescription("Test payment");
        
        testPayment = Payment.builder()
            .id("payment-123")
            .studentId("student-123")
            .amount(new BigDecimal("100.00"))
            .currency("USD")
            .method(PaymentMethod.STRIPE)
            .status(PaymentStatus.PENDING)
            .platformFee(new BigDecimal("10.00"))
            .netAmount(new BigDecimal("90.00"))
            .transactionId("TXN-TEST123")
            .createdAt(LocalDateTime.now())
            .build();
        
        testResponse = PaymentResponse.builder()
            .id("payment-123")
            .transactionId("pi_test123")
            .amount(new BigDecimal("100.00"))
            .currency("USD")
            .status(PaymentStatus.COMPLETED)
            .clientSecret("pi_test123_secret")
            .createdAt(LocalDateTime.now())
            .build();
    }
    
    @Test
    void createPayment_Success() {
        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);
        when(gatewayFactory.getGateway(any(PaymentMethod.class))).thenReturn(stripeGateway);
        when(stripeGateway.processPayment(any(Payment.class), any(PaymentRequest.class)))
            .thenReturn(testResponse);
        
        PaymentResponse result = paymentService.createPayment(testRequest);
        
        assertNotNull(result);
        assertEquals("payment-123", result.getId());
        assertEquals(PaymentStatus.COMPLETED, result.getStatus());
        verify(paymentRepository, times(2)).save(any(Payment.class));
    }
    
    @Test
    void createPayment_WithDiscount_Success() {
        testRequest.setDiscountCode("SAVE20");
        BigDecimal discountedAmount = new BigDecimal("80.00");
        
        when(discountService.applyDiscount(anyString(), any(BigDecimal.class), anyString()))
            .thenReturn(discountedAmount);
        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);
        when(gatewayFactory.getGateway(any(PaymentMethod.class))).thenReturn(stripeGateway);
        when(stripeGateway.processPayment(any(Payment.class), any(PaymentRequest.class)))
            .thenReturn(testResponse);
        
        PaymentResponse result = paymentService.createPayment(testRequest);
        
        assertNotNull(result);
        verify(discountService, times(1)).applyDiscount(eq("SAVE20"), any(BigDecimal.class), eq("student-123"));
    }
    
    @Test
    void getPayment_NotFound_ThrowsException() {
        when(paymentRepository.findById("invalid-id")).thenReturn(Optional.empty());
        
        assertThrows(PaymentException.class, () -> paymentService.getPayment("invalid-id"));
    }
    
    @Test
    void refundPayment_Success() {
        testPayment.setStatus(PaymentStatus.COMPLETED);
        testPayment.setExternalReference("pi_test123");
        
        when(paymentRepository.findById("payment-123")).thenReturn(Optional.of(testPayment));
        when(gatewayFactory.getGateway(any(PaymentMethod.class))).thenReturn(stripeGateway);
        doNothing().when(stripeGateway).refundPayment(anyString(), any(BigDecimal.class));
        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);
        
        Payment result = paymentService.refundPayment("payment-123", new BigDecimal("50.00"));
        
        assertNotNull(result);
        verify(stripeGateway, times(1)).refundPayment(eq("pi_test123"), eq(new BigDecimal("50.00")));
    }
}
