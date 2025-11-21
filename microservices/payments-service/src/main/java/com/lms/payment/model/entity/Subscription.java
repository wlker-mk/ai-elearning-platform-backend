package main.java.com.lms.payment.model.entity;

import com.lms.payment.model.enums.PaymentMethod;
import com.lms.payment.model.enums.SubscriptionType;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "subscriptions", indexes = {
    @Index(name = "idx_student_id", columnList = "studentId"),
    @Index(name = "idx_active_end_date", columnList = "isActive, endDate")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Subscription {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    
    @Column(unique = true, nullable = false)
    private String studentId;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private SubscriptionType type;
    
    @Column(nullable = false)
    private LocalDateTime startDate;
    
    @Column(nullable = false)
    private LocalDateTime endDate;
    
    private LocalDateTime trialEndDate;
    
    @Column(nullable = false)
    private Boolean isActive = true;
    
    @Column(nullable = false)
    private Boolean isCancelled = false;
    
    private LocalDateTime cancelledAt;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;
    
    @Column(nullable = false, length = 3)
    private String currency = "USD";
    
    @Column(nullable = false)
    private Boolean autoRenew = true;
    
    private LocalDateTime nextBillingDate;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentMethod paymentMethod;
    
    private String lastPaymentId;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Column(nullable = false)
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
