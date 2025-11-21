package main.java.com.lms.payment.controller;

import com.lms.payment.model.entity.Discount;
import com.lms.payment.service.DiscountService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/discounts")
@RequiredArgsConstructor
@Slf4j
public class DiscountController {
    
    private final DiscountService discountService;
    
    @PostMapping
    public ResponseEntity<Discount> createDiscount(@Valid @RequestBody Discount discount) {
        log.info("Creating discount: {}", discount.getCode());
        
        Discount created = discountService.createDiscount(discount);
        
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(created);
    }
}