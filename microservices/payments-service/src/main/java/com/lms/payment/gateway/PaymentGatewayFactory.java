package main.java.com.lms.payment.gateway;

import com.lms.payment.exception.PaymentException;
import com.lms.payment.model.enums.PaymentMethod;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class PaymentGatewayFactory {
    
    private final StripePaymentGateway stripeGateway;
    private final PayPalPaymentGateway paypalGateway;
    
    public PaymentGateway getGateway(PaymentMethod method) {
        return switch (method) {
            case STRIPE, CREDIT_CARD, DEBIT_CARD, APPLE_PAY, GOOGLE_PAY -> stripeGateway;
            case PAYPAL -> paypalGateway;
            default -> throw new PaymentException("Unsupported payment method: " + method);
        };
    }
    
    public PaymentGateway getGatewayByName(String gatewayName) {
        return switch (gatewayName.toLowerCase()) {
            case "stripe" -> stripeGateway;
            case "paypal" -> paypalGateway;
            default -> throw new PaymentException("Unknown gateway: " + gatewayName);
        };
    }
}