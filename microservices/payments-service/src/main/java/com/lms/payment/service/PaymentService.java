package com.lms.payment.service;

import com.lms.payment.dto.PaymentRequest;
import com.lms.payment.dto.PaymentResponse;
import com.lms.payment.exception.PaymentException;
import com.lms.payment.gateway.PaymentGateway;
import com.lms.payment.gateway.PaymentGatewayFactory;
import com.lms.payment.model.entity.Payment;
import com.lms.payment.model.enums.PaymentStatus;
import com.lms.payment.repository.PaymentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class PaymentService {
    
    private final PaymentRepository paymentRepository;
    private final PaymentGatewayFactory gatewayFactory;
    private final DiscountService discountService;
    
    @Value("${payment.platform.fee-percentage}")
    private Double platformFeePercentage;
    
    @Transactional
    public PaymentResponse createPayment(PaymentRequest request) {
        log.info("Creating payment for student: {}", request.getStudentId());
        
        try {
            // Apply discount if provided
            BigDecimal finalAmount = request.getAmount();
            if (request.getDiscountCode() != null) {
                finalAmount = discountService.applyDiscount(
                    request.getDiscountCode(),
                    request.getAmount(),
                    request.getStudentId()
                );
            }
            
            // Calculate fees
            BigDecimal platformFee = finalAmount.multiply(
                BigDecimal.valueOf(platformFeePercentage / 100)
            );
            BigDecimal netAmount = finalAmount.subtract(platformFee);
            
            // Create payment record
            Payment payment = Payment.builder()
                .studentId(request.getStudentId())
                .amount(finalAmount)
                .currency(request.getCurrency())
                .method(request.getMethod())
                .status(PaymentStatus.PENDING)
                .courseId(request.getCourseId())
                .subscriptionId(request.getSubscriptionId())
                .description(request.getDescription())
                .platformFee(platformFee)
                .netAmount(netAmount)
                .transactionId(generateTransactionId())
                .build();
            
            payment = paymentRepository.save(payment);
            
            // Process payment through gateway
            PaymentGateway gateway = gatewayFactory.getGateway(request.getMethod());
            PaymentResponse response = gateway.processPayment(payment, request);
            
            // Update payment status
            payment.setStatus(response.getStatus());
            payment.setExternalReference(response.getTransactionId());
            if (response.getStatus() == PaymentStatus.COMPLETED) {
                payment.setPaidAt(LocalDateTime.now());
            }
            paymentRepository.save(payment);
            
            log.info("Payment created successfully: {}", payment.getId());
            return response;
            
        } catch (Exception e) {
            log.error("Error creating payment: {}", e.getMessage(), e);
            throw new PaymentException("Failed to create payment: " + e.getMessage());
        }
    }
    
    public Payment getPayment(String paymentId) {
        return paymentRepository.findById(paymentId)
            .orElseThrow(() -> new PaymentException("Payment not found: " + paymentId));
    }
    
    public List<Payment> getPaymentsByStudent(String studentId) {
        return paymentRepository.findByStudentId(studentId);
    }
    
    @Transactional
    public Payment refundPayment(String paymentId, BigDecimal amount) {
        log.info("Processing refund for payment: {}", paymentId);
        
        Payment payment = getPayment(paymentId);
        
        if (payment.getStatus() != PaymentStatus.COMPLETED) {
            throw new PaymentException("Cannot refund payment that is not completed");
        }
        
        if (payment.getIsRefunded()) {
            throw new PaymentException("Payment already refunded");
        }
        
        // Process refund through gateway
        PaymentGateway gateway = gatewayFactory.getGateway(payment.getMethod());
        gateway.refundPayment(payment.getExternalReference(), amount);
        
        // Update payment
        payment.setStatus(PaymentStatus.REFUNDED);
        payment.setIsRefunded(true);
        payment.setRefundedAmount(amount);
        payment.setRefundedAt(LocalDateTime.now());
        
        payment = paymentRepository.save(payment);
        log.info("Payment refunded successfully: {}", paymentId);
        
        return payment;
    }
    
    @Transactional
    public void handleWebhook(String gateway, String payload, String signature) {
        log.info("Handling webhook from gateway: {}", gateway);
        
        try {
            PaymentGateway paymentGateway = gatewayFactory.getGatewayByName(gateway);
            paymentGateway.handleWebhook(payload, signature);
        } catch (Exception e) {
            log.error("Error handling webhook: {}", e.getMessage(), e);
            throw new PaymentException("Failed to handle webhook");
        }
    }
    
    private String generateTransactionId() {
        return "TXN-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }
}