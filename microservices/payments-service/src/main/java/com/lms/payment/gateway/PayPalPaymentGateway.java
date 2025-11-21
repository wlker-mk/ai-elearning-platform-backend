package main.java.com.lms.payment.gateway;

import com.lms.payment.dto.PaymentRequest;
import com.lms.payment.dto.PaymentResponse;
import com.lms.payment.exception.PaymentException;
import com.lms.payment.model.entity.Payment;
import com.lms.payment.model.enums.PaymentStatus;
import com.paypal.api.payments.*;
import com.paypal.base.rest.APIContext;
import com.paypal.base.rest.PayPalRESTException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Component
@Slf4j
public class PayPalPaymentGateway implements PaymentGateway {
    
    @Value("${payment.paypal.client-id}")
    private String clientId;
    
    @Value("${payment.paypal.client-secret}")
    private String clientSecret;
    
    @Value("${payment.paypal.mode}")
    private String mode;
    
    private APIContext getAPIContext() {
        return new APIContext(clientId, clientSecret, mode);
    }
    
    @Override
    public PaymentResponse processPayment(Payment payment, PaymentRequest request) {
        log.info("Processing PayPal payment: {}", payment.getId());
        
        try {
            // Create amount
            Amount amount = new Amount();
            amount.setCurrency(payment.getCurrency());
            amount.setTotal(payment.getAmount().toString());
            
            // Create transaction
            Transaction transaction = new Transaction();
            transaction.setDescription(payment.getDescription());
            transaction.setAmount(amount);
            
            List<Transaction> transactions = new ArrayList<>();
            transactions.add(transaction);
            
            // Create payer
            Payer payer = new Payer();
            payer.setPaymentMethod("paypal");
            
            // Create payment
            com.paypal.api.payments.Payment paypalPayment = 
                new com.paypal.api.payments.Payment();
            paypalPayment.setIntent("sale");
            paypalPayment.setPayer(payer);
            paypalPayment.setTransactions(transactions);
            
            // Set redirect URLs
            RedirectUrls redirectUrls = new RedirectUrls();
            redirectUrls.setCancelUrl("http://localhost:3000/payment/cancel");
            redirectUrls.setReturnUrl("http://localhost:3000/payment/success");
            paypalPayment.setRedirectUrls(redirectUrls);
            
            // Create payment
            com.paypal.api.payments.Payment createdPayment = 
                paypalPayment.create(getAPIContext());
            
            // Get approval URL
            String approvalUrl = createdPayment.getLinks().stream()
                .filter(link -> link.getRel().equals("approval_url"))
                .findFirst()
                .map(Links::getHref)
                .orElse(null);
            
            log.info("PayPal payment created: {}", createdPayment.getId());
            
            return PaymentResponse.builder()
                .id(payment.getId())
                .transactionId(createdPayment.getId())
                .amount(payment.getAmount())
                .currency(payment.getCurrency())
                .status(PaymentStatus.PENDING)
                .redirectUrl(approvalUrl)
                .createdAt(payment.getCreatedAt())
                .build();
                
        } catch (PayPalRESTException e) {
            log.error("PayPal payment failed: {}", e.getMessage(), e);
            throw new PaymentException("PayPal payment failed: " + e.getMessage());
        }
    }
    
    @Override
    public void refundPayment(String transactionId, BigDecimal amount) {
        log.info("Processing PayPal refund for: {}", transactionId);
        
        try {
            // Get the sale
            Sale sale = Sale.get(getAPIContext(), transactionId);
            
            // Create refund
            RefundRequest refundRequest = new RefundRequest();
            Amount refundAmount = new Amount();
            refundAmount.setCurrency("USD");
            refundAmount.setTotal(amount.toString());
            refundRequest.setAmount(refundAmount);
            
            DetailedRefund refund = sale.refund(getAPIContext(), refundRequest);
            
            log.info("PayPal refund created: {}", refund.getId());
            
        } catch (PayPalRESTException e) {
            log.error("PayPal refund failed: {}", e.getMessage(), e);
            throw new PaymentException("PayPal refund failed: " + e.getMessage());
        }
    }
    
    @Override
    public void handleWebhook(String payload, String signature) {
        log.info("Handling PayPal webhook");
        
        try {
            // Verify webhook signature
            // Process webhook events
            // Update payment status accordingly
            
        } catch (Exception e) {
            log.error("Error handling PayPal webhook: {}", e.getMessage(), e);
            throw new PaymentException("Failed to handle webhook");
        }
    }
    
    public PaymentStatus executePayment(String paymentId, String payerId) {
        log.info("Executing PayPal payment: {}", paymentId);
        
        try {
            com.paypal.api.payments.Payment payment = 
                new com.paypal.api.payments.Payment();
            payment.setId(paymentId);
            
            PaymentExecution paymentExecution = new PaymentExecution();
            paymentExecution.setPayerId(payerId);
            
            com.paypal.api.payments.Payment executedPayment = 
                payment.execute(getAPIContext(), paymentExecution);
            
            log.info("PayPal payment executed: {}", executedPayment.getState());
            
            return "approved".equals(executedPayment.getState()) 
                ? PaymentStatus.COMPLETED 
                : PaymentStatus.FAILED;
                
        } catch (PayPalRESTException e) {
            log.error("PayPal execution failed: {}", e.getMessage(), e);
            throw new PaymentException("PayPal execution failed: " + e.getMessage());
        }
    }
}