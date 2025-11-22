package com.lms.payment.model.entity;

import com.lms.payment.model.enums.PaymentMethod;
import com.lms.payment.model.enums.PaymentStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "payments", indexes = {
    @Index(name = "idx_student_status", columnList = "studentId, status"),
    @Index(name = "idx_transaction_id", columnList = "transactionId")
})
@Data
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Payment {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    
    @Column(nullable = false)
    private String studentId;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;
    
    @Builder.Default
    @Column(nullable = false, length = 3)
    private String currency = "USD";
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentMethod method;
    
    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status = PaymentStatus.PENDING;
    
    @Column(unique = true)
    private String transactionId;
    
    private String externalReference;
    
    @Column(columnDefinition = "jsonb")
    private String gatewayResponse;
    
    private String courseId;
    
    private String subscriptionId;
    
    @Column(columnDefinition = "jsonb")
    private String items;
    
    private String description;
    
    @Column(columnDefinition = "jsonb")
    private String metadata;

    @Builder.Default
    @Column(precision = 10, scale = 2)
    private BigDecimal processingFee = BigDecimal.ZERO;
    
    @Builder.Default
    @Column(precision = 10, scale = 2)
    private BigDecimal platformFee = BigDecimal.ZERO;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal netAmount;
    
    @Builder.Default
    @Column(nullable = false)
    private Boolean isRefunded = false;
    
    @Column(precision = 10, scale = 2)
    private BigDecimal refundedAmount;
    
    private LocalDateTime refundedAt;
    
    private LocalDateTime paidAt;
    
    @Builder.Default
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Builder.Default
    @Column(nullable = false)
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    public void setStatus(PaymentStatus paymentStatus) {
        throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    public void setExternalReference(String pi_test123) {
        throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }
    
    
}