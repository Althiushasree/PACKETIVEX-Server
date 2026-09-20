package com.example.packetivex.controller;

import com.example.packetivex.dto.CaptureResponse;
import com.example.packetivex.dto.CaptureStartRequest;
import com.example.packetivex.model.CaptureSession;
import com.example.packetivex.repository.CaptureSessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;
import java.util.Map;

@RestController
@RequestMapping("/api/capture")
@RequiredArgsConstructor
public class CaptureController {
    private final CaptureSessionRepository sessionRepository;

    @PostMapping("/start")
    public ResponseEntity<CaptureResponse> startCapture(@RequestBody CaptureStartRequest request) {
        String sid = UUID.randomUUID().toString();
        CaptureSession session = new CaptureSession();
        session.setSessionId(sid);
        session.setStartTime(System.currentTimeMillis());
        session.setInterfaceName(request.getInterfaceName());
        session.setInterfaceType(request.getInterfaceType());
        session.setSsid(request.getSsid());
        session.setLocalIp(request.getLocalIpv4());
        session.setGateway(request.getGateway());
        session.setDns(request.getDns());
        session.setStatus("ACTIVE");
        sessionRepository.save(session);
        return ResponseEntity.ok(new CaptureResponse(sid, "SUCCESS"));
    }

    @PostMapping("/end")
    public ResponseEntity<Map<String, String>> endCapture(@RequestBody Map<String, String> request) {
        String sid = request.get("sessionId");
        CaptureSession session = sessionRepository.findById(sid).orElse(null);
        if (session != null) {
          session.setEndTime(System.currentTimeMillis());
          session.setStatus("COMPLETED");
          sessionRepository.save(session);
        }
        return ResponseEntity.ok(Map.of("status", "SUCCESS"));
    }
}
