package com.example.packetivex.repository;

import com.example.packetivex.model.CaptureSession;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CaptureSessionRepository extends JpaRepository<CaptureSession, String> {
}
