package com.example.packetivex.repository;

import com.example.packetivex.model.Application;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ApplicationRepository extends JpaRepository<Application, Long> {
    Optional<Application> findByPackageName(String packageName);
}
