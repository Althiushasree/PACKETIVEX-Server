package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
@Builder
public class DashboardResponse {
    private Long totalPackets;
    private Long totalBytes;
    private Integer activeConnections;
    private Integer openSockets;
    private Integer totalAlarms;
}
