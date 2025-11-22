package com.lms.payment.controller;

import com.lms.payment.service.PaymentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/webhooks")
@RequiredArgsConstructor
@Slf4j
public class WebhookController {
    
    private final PaymentService paymentService;
    
    @PostMapping("/stripe")
    public ResponseEntity<Void> handleStripeWebhook(
            @RequestBody String payload,
            @RequestHeader("Stripe-Signature") String signature) {
        log.info("Received Stripe webhook");
        
        try {
            paymentService.handleWebhook("stripe", payload, signature);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            log.error("Error processing Stripe webhook: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    @PostMapping("/paypal")
    public ResponseEntity<Void> handlePayPalWebhook(
            @RequestBody String payload,
            @RequestHeader("PAYPAL-TRANSMISSION-SIG") String signature) {
        log.info("Received PayPal webhook");
        
        try {
            paymentService.handleWebhook("paypal", payload, signature);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            log.error("Error processing PayPal webhook: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}