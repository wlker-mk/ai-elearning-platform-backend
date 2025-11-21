package main.java.com.lms.payment.repository;

import com.lms.payment.model.entity.Discount;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface DiscountRepository extends JpaRepository<Discount, String> {
    
    Optional<Discount> findByCode(String code);
    
    List<Discount> findByStartDateBeforeAndEndDateAfter(LocalDateTime now1, LocalDateTime now2);
}
