package main.java.com.lms.payment.gateway;

import com.lms.payment.dto.PaymentRequest;
import com.lms.payment.dto.PaymentResponse;
import com.lms.payment.model.entity.Payment;

import java.math.BigDecimal;

public interface PaymentGateway {
    PaymentResponse processPayment(Payment payment, PaymentRequest request);
    void refundPayment(String transactionId, BigDecimal amount);
    void handleWebhook(String payload, String signature);
}
