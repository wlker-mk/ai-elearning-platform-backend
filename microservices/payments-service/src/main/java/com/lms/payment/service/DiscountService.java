package com.lms.payment.service;

import com.lms.payment.exception.DiscountException;
import com.lms.payment.model.entity.Discount;
import com.lms.payment.model.enums.DiscountType;
import com.lms.payment.repository.DiscountRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@SuppressWarnings("unused")
@Service
@RequiredArgsConstructor
@Slf4j
public class DiscountService {
    
    private final DiscountRepository discountRepository;
    
    @Transactional
    public BigDecimal applyDiscount(String code, BigDecimal amount, String studentId) {
        log.info("Applying discount code: {}", code);
        
        Discount discount = discountRepository.findByCode(code)
            .orElseThrow(() -> new DiscountException("Invalid discount code"));
        
        // Validate discount
        validateDiscount(discount);
        
        // Calculate discounted amount
        BigDecimal discountedAmount = calculateDiscountedAmount(discount, amount);
        
        // Update usage count
        discount.setUsesCount(discount.getUsesCount() + 1);
        discountRepository.save(discount);
        
        log.info("Discount applied successfully. Original: {}, Discounted: {}", 
                amount, discountedAmount);
        
        return discountedAmount;
    }
    
    private void validateDiscount(Discount discount) {
        LocalDateTime now = LocalDateTime.now();
        
        // Check if discount is active
        if (now.isBefore(discount.getStartDate())) {
            throw new DiscountException("Discount has not started yet");
        }
        
        if (now.isAfter(discount.getEndDate())) {
            throw new DiscountException("Discount has expired");
        }
        
        // Check usage limits
        if (discount.getMaxUses() != null && 
            discount.getUsesCount() >= discount.getMaxUses()) {
            throw new DiscountException("Discount usage limit reached");
        }
    }
    
    private BigDecimal calculateDiscountedAmount(Discount discount, BigDecimal amount) {
        return switch (discount.getType()) {
            case PERCENTAGE -> {
                BigDecimal percentage = discount.getValue().divide(BigDecimal.valueOf(100));
                BigDecimal discountAmount = amount.multiply(percentage);
                yield amount.subtract(discountAmount);
            }
            case FIXED_AMOUNT -> {
                BigDecimal result = amount.subtract(discount.getValue());
                yield result.max(BigDecimal.ZERO);
            }
            default -> amount;
        };
    }
    
    public Discount createDiscount(Discount discount) {
        log.info("Creating discount: {}", discount.getCode());
        
        // Check if code already exists
        if (discountRepository.findByCode(discount.getCode()).isPresent()) {
            throw new DiscountException("Discount code already exists");
        }
        
        return discountRepository.save(discount);
    }
}