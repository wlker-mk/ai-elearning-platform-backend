package main.java.com.lms.payment.controller;

import com.lms.payment.dto.PaymentRequest;
import com.lms.payment.dto.PaymentResponse;
import com.lms.payment.model.entity.Payment;
import com.lms.payment.service.PaymentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/payments")
@RequiredArgsConstructor
@Slf4j
public class PaymentController {
    
    private final PaymentService paymentService;
    
    @PostMapping
    public ResponseEntity<PaymentResponse> createPayment(
            @Valid @RequestBody PaymentRequest request) {
        log.info("Creating payment for student: {}", request.getStudentId());
        
        PaymentResponse response = paymentService.createPayment(request);
        
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(response);
    }
    
    @GetMapping("/{paymentId}")
    public ResponseEntity<Payment> getPayment(@PathVariable String paymentId) {
        log.info("Fetching payment: {}", paymentId);
        
        Payment payment = paymentService.getPayment(paymentId);
        
        return ResponseEntity.ok(payment);
    }
    
    @GetMapping("/student/{studentId}")
    public ResponseEntity<List<Payment>> getStudentPayments(@PathVariable String studentId) {
        log.info("Fetching payments for student: {}", studentId);
        
        List<Payment> payments = paymentService.getPaymentsByStudent(studentId);
        
        return ResponseEntity.ok(payments);
    }
    
    @PostMapping("/{paymentId}/refund")
    public ResponseEntity<Payment> refundPayment(
            @PathVariable String paymentId,
            @RequestParam(required = false) BigDecimal amount) {
        log.info("Processing refund for payment: {}", paymentId);
        
        Payment payment = paymentService.refundPayment(paymentId, amount);
        
        return ResponseEntity.ok(payment);
    }
}