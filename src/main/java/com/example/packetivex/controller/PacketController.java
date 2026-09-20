package com.example.packetivex.controller;

import com.example.packetivex.dto.PacketDto;
import com.example.packetivex.model.Application;
import com.example.packetivex.model.Packet;
import com.example.packetivex.repository.ApplicationRepository;
import com.example.packetivex.repository.CaptureSessionRepository;
import com.example.packetivex.repository.PacketRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/packets")
@RequiredArgsConstructor
public class PacketController {
    private final PacketRepository packetRepository;
    private final CaptureSessionRepository sessionRepository;
    private final ApplicationRepository applicationRepository;

    @PostMapping
    public ResponseEntity<Map<String, String>> uploadPacket(@RequestBody PacketDto dto) {
        Packet packet = new Packet();
        sessionRepository.findById(dto.getSessionId()).ifPresent(packet::setSession);
        packet.setTimestamp(dto.getTimestamp());
        packet.setSourceIp(dto.getSourceIp());
        packet.setDestIp(dto.getDestIp());
        packet.setSourcePort(dto.getSourcePort());
        packet.setDestPort(dto.getDestPort());
        packet.setProtocol(dto.getProtocol());
        packet.setLength(dto.getLength());
        packet.setAppName(dto.getAppName());
        packet.setPackageName(dto.getAppPackage());
        packet.setHostname(dto.getHostname());
        packet.setHttpMethod(dto.getHttpMethod());
        packet.setUrl(dto.getUrl());
        packet.setTlsSni(dto.getTlsSni());
        // Payload conversion from Hex if needed
        packetRepository.save(packet);

        // Update application stats
        Application app = applicationRepository.findByPackageName(dto.getAppPackage()).orElse(new Application());
        if (app.getPackageName() == null) {
            app.setName(dto.getAppName());
            app.setPackageName(dto.getAppPackage());
            app.setTotalBytes(0L);
        }
        app.setTotalBytes(app.getTotalBytes() + dto.getLength());
        applicationRepository.save(app);

        return ResponseEntity.ok(Map.of("status", "OK"));
    }
}
