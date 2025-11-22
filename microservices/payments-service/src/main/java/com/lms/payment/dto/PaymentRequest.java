package com.lms.payment.dto;

import com.lms.payment.model.enums.PaymentMethod;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PaymentRequest {
    
    @NotNull(message = "Student ID is required")
    private String studentId;
    
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    private BigDecimal amount;
    
    @NotBlank(message = "Currency is required")
    @Size(min = 3, max = 3, message = "Currency must be 3 characters")
    private String currency = "USD";
    
    @NotNull(message = "Payment method is required")
    private PaymentMethod method;
    
    private String courseId;
    
    private String subscriptionId;
    
    private String discountCode;
    
    private String description;
    
    private Map<String, Object> metadata;
    
    // Payment method specific fields
    private String cardToken;
    private String paypalOrderId;
}

