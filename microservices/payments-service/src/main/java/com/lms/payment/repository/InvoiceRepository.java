package main.java.com.lms.payment.repository;

import com.lms.payment.model.entity.Invoice;
import com.lms.payment.model.enums.PaymentStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface InvoiceRepository extends JpaRepository<Invoice, String> {
    
    Optional<Invoice> findByInvoiceNumber(String invoiceNumber);
    
    List<Invoice> findByStudentId(String studentId);
    
    List<Invoice> findByStudentIdAndStatus(String studentId, PaymentStatus status);
    
    List<Invoice> findByStatusAndDueDateBefore(PaymentStatus status, LocalDateTime dueDate);
    
    List<Invoice> findByPaymentId(String paymentId);
}

