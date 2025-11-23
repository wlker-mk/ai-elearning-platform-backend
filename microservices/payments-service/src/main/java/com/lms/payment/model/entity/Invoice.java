package com.lms.payment.model.entity;

import com.lms.payment.model.enums.PaymentStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;




@Entity
@Table(name = "invoices", indexes = {
    @Index(name = "idx_invoice_number", columnList = "invoiceNumber"),
    @Index(name = "idx_student_status", columnList = "studentId, status")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor

public class Invoice {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    
    @Column(unique = true, nullable = false)
    private String invoiceNumber;
    
    @Column(nullable = false)
    private String studentId;
    
    private String paymentId;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal subtotal;
    
    @Builder.Default
    @Column(precision = 10, scale = 2)
    private BigDecimal tax = BigDecimal.ZERO;
    
    @Builder.Default
    @Column(precision = 10, scale = 2)
    private BigDecimal discount = BigDecimal.ZERO;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal total;
    
    @Builder.Default
    @Column(precision = 10, scale = 2)
    private BigDecimal amountPaid = BigDecimal.ZERO;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amountDue;
    
    @Builder.Default
    @Column(nullable = false, length = 3)
    private String currency = "USD";
    
    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status = PaymentStatus.PENDING;
    
    @Column(columnDefinition = "jsonb", nullable = false)
    private String items;
    
    @Builder.Default
    @Column(nullable = false)
    private LocalDateTime issueDate = LocalDateTime.now();
    
    @Column(nullable = false)
    private LocalDateTime dueDate;
    
    private LocalDateTime paidAt;
    
    private String pdfUrl;
    
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
}
