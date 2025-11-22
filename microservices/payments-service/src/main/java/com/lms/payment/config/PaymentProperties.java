package com.lms.payment.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "payment")
@Data
public class PaymentProperties {
    
    private Stripe stripe = new Stripe();
    private Paypal paypal = new Paypal();
    private Platform platform = new Platform();
    
    @Data
    public static class Stripe {
        private String apiKey;
        private String webhookSecret;
        private String publishableKey;
    }
    
    @Data
    public static class Paypal {
        private String clientId;
        private String clientSecret;
        private String mode = "sandbox";
    }
    
    @Data
    public static class Platform {
        private Double feePercentage = 10.0;
        private String currency = "USD";
    }
}
