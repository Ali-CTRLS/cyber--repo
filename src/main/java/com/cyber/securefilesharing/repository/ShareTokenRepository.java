package com.cyber.securefilesharing.repository;

import com.cyber.securefilesharing.model.ShareToken;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ShareTokenRepository extends JpaRepository<ShareToken, Long> {
    Optional<ShareToken> findByToken(String token);
}
