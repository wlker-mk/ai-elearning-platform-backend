package com.lms.payment.dto;

import com.lms.payment.model.enums.PaymentMethod;
import com.lms.payment.model.enums.SubscriptionType;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SubscriptionRequest {
    
    @NotNull(message = "Student ID is required")
    private String studentId;
    
    @NotNull(message = "Subscription type is required")
    private SubscriptionType type;
    
    @NotNull(message = "Payment method is required")
    private PaymentMethod paymentMethod;
    
    private String cardToken;
    
    private Boolean autoRenew = true;
}
