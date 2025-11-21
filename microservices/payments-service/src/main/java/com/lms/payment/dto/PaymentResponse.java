package main.java.com.lms.payment.dto;

import com.lms.payment.model.enums.PaymentStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PaymentResponse {
    private String id;
    private String transactionId;
    private BigDecimal amount;
    private String currency;
    private PaymentStatus status;
    private String description;
    private LocalDateTime createdAt;
    private String clientSecret; // For Stripe
    private String redirectUrl; // For PayPal
}

