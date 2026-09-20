package com.example.packetivex.controller;

import com.example.packetivex.dto.*;
import com.example.packetivex.model.Application;
import com.example.packetivex.repository.ApplicationRepository;
import com.example.packetivex.repository.PacketRepository;
import com.example.packetivex.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class DashboardController {
    private final PacketRepository packetRepository;
    private final ApplicationRepository applicationRepository;
    private final AlertRepository alertRepository;

    @GetMapping("/dashboard")
    public ResponseEntity<DashboardResponse> getDashboard() {
        long totalPackets = packetRepository.count();
        long totalBytes = applicationRepository.findAll().stream().mapToLong(Application::getTotalBytes).sum();
        
        return ResponseEntity.ok(DashboardResponse.builder()
                .totalPackets(totalPackets)
                .totalBytes(totalBytes)
                .activeConnections(12)
                .openSockets(8)
                .totalAlarms((int) alertRepository.count())
                .build());
    }

    @GetMapping("/analytics/dashboard")
    public ResponseEntity<AnalyticsDashboardResponse> getAnalytics() {
        return ResponseEntity.ok(AnalyticsDashboardResponse.builder()
                .protocolDistribution(List.of())
                .topApps(List.of())
                .timelinePoints(List.of())
                .highestConsumer("WhatsApp")
                .build());
    }

    @GetMapping("/analytics/applications")
    public ResponseEntity<List<AppTrafficSummary>> getApplications() {
        List<AppTrafficSummary> apps = applicationRepository.findAll().stream()
                .sorted((a, b) -> b.getTotalBytes().compareTo(a.getTotalBytes()))
                .map(a -> new AppTrafficSummary(a.getName(), a.getPackageName(), 0, a.getTotalBytes(), 0.0f))
                .collect(Collectors.toList());
        return ResponseEntity.ok(apps);
    }

    @GetMapping("/analytics/ips")
    public ResponseEntity<List<Object>> getIps() {
        return ResponseEntity.ok(List.of());
    }
}
