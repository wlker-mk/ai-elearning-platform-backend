package com.lms.payment.gateway;

import com.lms.payment.dto.PaymentRequest;
import com.lms.payment.dto.PaymentResponse;
import com.lms.payment.exception.PaymentException;
import com.lms.payment.model.entity.Payment;
import com.lms.payment.model.enums.PaymentStatus;
import com.stripe.Stripe;
import com.stripe.exception.StripeException;
import com.stripe.model.PaymentIntent;
import com.stripe.model.Refund;
import com.stripe.net.Webhook;
import com.stripe.param.PaymentIntentCreateParams;
import com.stripe.param.RefundCreateParams;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Component
@Slf4j
public class StripePaymentGateway implements PaymentGateway {
    
    @Value("${payment.stripe.api-key}")
    private String apiKey;
    
    @Value("${payment.stripe.webhook-secret}")
    private String webhookSecret;
    
    @PostConstruct
    public void init() {
        Stripe.apiKey = apiKey;
    }
    
    @Override
    public PaymentResponse processPayment(Payment payment, PaymentRequest request) {
        log.info("Processing Stripe payment: {}", payment.getId());
        
        try {
            // Convert amount to cents (Stripe uses smallest currency unit)
            long amountInCents = payment.getAmount()
                .multiply(BigDecimal.valueOf(100))
                .longValue();
            
            // Create payment intent
            PaymentIntentCreateParams params = PaymentIntentCreateParams.builder()
                .setAmount(amountInCents)
                .setCurrency(payment.getCurrency().toLowerCase())
                .setDescription(payment.getDescription())
                .putMetadata("payment_id", payment.getId())
                .putMetadata("student_id", payment.getStudentId())
                .setAutomaticPaymentMethods(
                    PaymentIntentCreateParams.AutomaticPaymentMethods.builder()
                        .setEnabled(true)
                        .build()
                )
                .build();
            
            PaymentIntent intent = PaymentIntent.create(params);
            
            log.info("Stripe PaymentIntent created: {}", intent.getId());
            
            return PaymentResponse.builder()
                .id(payment.getId())
                .transactionId(intent.getId())
                .amount(payment.getAmount())
                .currency(payment.getCurrency())
                .status(mapStripeStatus(intent.getStatus()))
                .clientSecret(intent.getClientSecret())
                .createdAt(payment.getCreatedAt())
                .build();
                
        } catch (StripeException e) {
            log.error("Stripe payment failed: {}", e.getMessage(), e);
            throw new PaymentException("Stripe payment failed: " + e.getMessage());
        }
    }
    
    @Override
    public void refundPayment(String transactionId, BigDecimal amount) {
        log.info("Processing Stripe refund for: {}", transactionId);
        
        try {
            long amountInCents = amount.multiply(BigDecimal.valueOf(100)).longValue();
            
            RefundCreateParams params = RefundCreateParams.builder()
                .setPaymentIntent(transactionId)
                .setAmount(amountInCents)
                .build();
            
            Refund refund = Refund.create(params);
            
            log.info("Stripe refund created: {}", refund.getId());
            
        } catch (StripeException e) {
            log.error("Stripe refund failed: {}", e.getMessage(), e);
            throw new PaymentException("Stripe refund failed: " + e.getMessage());
        }
    }
    
    @Override
    public void handleWebhook(String payload, String signature) {
        log.info("Handling Stripe webhook");
        
        try {
            com.stripe.model.Event event = Webhook.constructEvent(
                payload, signature, webhookSecret
            );
            
            switch (event.getType()) {
                case "payment_intent.succeeded":
                    handlePaymentSuccess(event);
                    break;
                case "payment_intent.payment_failed":
                    handlePaymentFailure(event);
                    break;
                case "charge.refunded":
                    handleRefund(event);
                    break;
                default:
                    log.info("Unhandled webhook event type: {}", event.getType());
            }
            
        } catch (Exception e) {
            log.error("Error handling Stripe webhook: {}", e.getMessage(), e);
            throw new PaymentException("Failed to handle webhook");
        }
    }
    
    private void handlePaymentSuccess(com.stripe.model.Event event) {
        log.info("Handling payment success webhook");
        // Update payment status in database
    }
    
    private void handlePaymentFailure(com.stripe.model.Event event) {
        log.info("Handling payment failure webhook");
        // Update payment status and notify user
    }
    
    private void handleRefund(com.stripe.model.Event event) {
        log.info("Handling refund webhook");
        // Update payment refund status
    }
    
    private PaymentStatus mapStripeStatus(String stripeStatus) {
        return switch (stripeStatus) {
            case "succeeded" -> PaymentStatus.COMPLETED;
            case "processing" -> PaymentStatus.PROCESSING;
            case "requires_payment_method", "requires_confirmation", "requires_action" -> 
                PaymentStatus.PENDING;
            case "canceled" -> PaymentStatus.CANCELLED;
            default -> PaymentStatus.FAILED;
        };
    }
}
