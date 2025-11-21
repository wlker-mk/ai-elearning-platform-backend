package main.java.com.lms.payment.service;

import com.lms.payment.dto.SubscriptionRequest;
import com.lms.payment.exception.SubscriptionException;
import com.lms.payment.model.entity.Subscription;
import com.lms.payment.model.enums.SubscriptionType;
import com.lms.payment.repository.SubscriptionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class SubscriptionService {
    
    private final SubscriptionRepository subscriptionRepository;
    private final PaymentService paymentService;
    
    private static final Map<SubscriptionType, Integer> SUBSCRIPTION_DURATIONS = Map.of(
        SubscriptionType.MONTHLY, 1,
        SubscriptionType.QUARTERLY, 3,
        SubscriptionType.SEMI_ANNUAL, 6,
        SubscriptionType.ANNUAL, 12
    );
    
    private static final Map<SubscriptionType, BigDecimal> SUBSCRIPTION_PRICES = Map.of(
        SubscriptionType.MONTHLY, new BigDecimal("9.99"),
        SubscriptionType.QUARTERLY, new BigDecimal("24.99"),
        SubscriptionType.SEMI_ANNUAL, new BigDecimal("44.99"),
        SubscriptionType.ANNUAL, new BigDecimal("79.99"),
        SubscriptionType.STUDENT, new BigDecimal("4.99"),
        SubscriptionType.LIFETIME, new BigDecimal("299.99")
    );
    
    @Transactional
    public Subscription createSubscription(SubscriptionRequest request) {
        log.info("Creating subscription for student: {}", request.getStudentId());
        
        // Check if student already has active subscription
        subscriptionRepository.findByStudentId(request.getStudentId())
            .ifPresent(sub -> {
                if (sub.getIsActive()) {
                    throw new SubscriptionException("Student already has an active subscription");
                }
            });
        
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime startDate = now;
        LocalDateTime endDate = calculateEndDate(request.getType(), startDate);
        BigDecimal price = SUBSCRIPTION_PRICES.get(request.getType());
        
        Subscription subscription = Subscription.builder()
            .studentId(request.getStudentId())
            .type(request.getType())
            .startDate(startDate)
            .endDate(endDate)
            .price(price)
            .paymentMethod(request.getPaymentMethod())
            .autoRenew(request.getAutoRenew())
            .isActive(true)
            .build();
        
        // Set next billing date if auto-renew
        if (request.getAutoRenew() && !request.getType().equals(SubscriptionType.LIFETIME)) {
            subscription.setNextBillingDate(endDate);
        }
        
        subscription = subscriptionRepository.save(subscription);
        log.info("Subscription created successfully: {}", subscription.getId());
        
        return subscription;
    }
    
    @Transactional
    public Subscription cancelSubscription(String subscriptionId) {
        log.info("Cancelling subscription: {}", subscriptionId);
        
        Subscription subscription = subscriptionRepository.findById(subscriptionId)
            .orElseThrow(() -> new SubscriptionException("Subscription not found"));
        
        subscription.setIsCancelled(true);
        subscription.setCancelledAt(LocalDateTime.now());
        subscription.setAutoRenew(false);
        
        subscription = subscriptionRepository.save(subscription);
        log.info("Subscription cancelled successfully");
        
        return subscription;
    }
    
    @Scheduled(cron = "0 0 2 * * *") // Run at 2 AM every day
    @Transactional
    public void processAutoRenewals() {
        log.info("Processing subscription auto-renewals");
        
        LocalDateTime tomorrow = LocalDateTime.now().plusDays(1);
        List<Subscription> subscriptionsToRenew = 
            subscriptionRepository.findByIsActiveTrueAndAutoRenewTrueAndNextBillingDateBefore(tomorrow);
        
        for (Subscription subscription : subscriptionsToRenew) {
            try {
                renewSubscription(subscription);
            } catch (Exception e) {
                log.error("Failed to renew subscription: {}", subscription.getId(), e);
            }
        }
        
        log.info("Processed {} subscriptions for renewal", subscriptionsToRenew.size());
    }
    
    @Scheduled(cron = "0 0 3 * * *") // Run at 3 AM every day
    @Transactional
    public void deactivateExpiredSubscriptions() {
        log.info("Deactivating expired subscriptions");
        
        LocalDateTime now = LocalDateTime.now();
        List<Subscription> expiredSubscriptions = 
            subscriptionRepository.findByIsActiveTrueAndEndDateBefore(now);
        
        for (Subscription subscription : expiredSubscriptions) {
            if (!subscription.getAutoRenew()) {
                subscription.setIsActive(false);
                subscriptionRepository.save(subscription);
                log.info("Deactivated subscription: {}", subscription.getId());
            }
        }
        
        log.info("Deactivated {} expired subscriptions", expiredSubscriptions.size());
    }
    
    private void renewSubscription(Subscription subscription) {
        log.info("Renewing subscription: {}", subscription.getId());
        
        // Process payment for renewal
        // This would trigger a payment through the payment service
        
        // Update subscription dates
        LocalDateTime newStartDate = subscription.getEndDate();
        LocalDateTime newEndDate = calculateEndDate(subscription.getType(), newStartDate);
        
        subscription.setStartDate(newStartDate);
        subscription.setEndDate(newEndDate);
        subscription.setNextBillingDate(newEndDate);
        
        subscriptionRepository.save(subscription);
        log.info("Subscription renewed successfully");
    }
    
    private LocalDateTime calculateEndDate(SubscriptionType type, LocalDateTime startDate) {
        if (type == SubscriptionType.LIFETIME) {
            return startDate.plusYears(100); // Effectively lifetime
        }
        
        Integer months = SUBSCRIPTION_DURATIONS.get(type);
        if (months == null) {
            throw new SubscriptionException("Invalid subscription type");
        }
        
        return startDate.plusMonths(months);
    }
}