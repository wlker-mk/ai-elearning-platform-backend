package main.java.com.lms.payment.controller;

import com.lms.payment.dto.SubscriptionRequest;
import com.lms.payment.model.entity.Subscription;
import com.lms.payment.service.SubscriptionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/subscriptions")
@RequiredArgsConstructor
@Slf4j
public class SubscriptionController {
    
    private final SubscriptionService subscriptionService;
    
    @PostMapping
    public ResponseEntity<Subscription> createSubscription(
            @Valid @RequestBody SubscriptionRequest request) {
        log.info("Creating subscription for student: {}", request.getStudentId());
        
        Subscription subscription = subscriptionService.createSubscription(request);
        
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(subscription);
    }
    
    @PostMapping("/{subscriptionId}/cancel")
    public ResponseEntity<Subscription> cancelSubscription(
            @PathVariable String subscriptionId) {
        log.info("Cancelling subscription: {}", subscriptionId);
        
        Subscription subscription = subscriptionService.cancelSubscription(subscriptionId);
        
        return ResponseEntity.ok(subscription);
    }
}