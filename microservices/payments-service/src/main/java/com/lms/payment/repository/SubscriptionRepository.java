package com.lms.payment.repository;

import com.lms.payment.model.entity.Subscription;
import com.lms.payment.model.enums.SubscriptionType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface SubscriptionRepository extends JpaRepository<Subscription, String> {
    
    Optional<Subscription> findByStudentId(String studentId);
    
    List<Subscription> findByIsActiveTrue();
    
    List<Subscription> findByIsActiveTrueAndEndDateBefore(LocalDateTime endDate);
    
    List<Subscription> findByIsActiveTrueAndAutoRenewTrueAndNextBillingDateBefore(LocalDateTime date);
    
    List<Subscription> findByType(SubscriptionType type);
}

