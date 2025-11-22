package com.lms.payment.repository;

import com.lms.payment.model.entity.Payment;
import com.lms.payment.model.enums.PaymentStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface PaymentRepository extends JpaRepository<Payment, String> {
    
    List<Payment> findByStudentId(String studentId);
    
    List<Payment> findByStudentIdAndStatus(String studentId, PaymentStatus status);
    
    Optional<Payment> findByTransactionId(String transactionId);
    
    Optional<Payment> findByExternalReference(String externalReference);
    
    List<Payment> findByStatusAndCreatedAtBefore(PaymentStatus status, LocalDateTime dateTime);
    
    @Query("SELECT p FROM Payment p WHERE p.studentId = :studentId " +
        "AND p.createdAt BETWEEN :startDate AND :endDate")
    List<Payment> findByStudentIdAndDateRange(String studentId, 
                                        LocalDateTime startDate, 
                                        LocalDateTime endDate);
    
    @Query("SELECT SUM(p.amount) FROM Payment p WHERE p.studentId = :studentId " +
        "AND p.status = 'COMPLETED'")
    Double getTotalSpentByStudent(String studentId);
}