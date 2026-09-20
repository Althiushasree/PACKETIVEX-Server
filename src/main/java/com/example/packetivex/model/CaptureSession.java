package com.example.packetivex.model;

import jakarta.persistence.*;
import lombok.*;
import java.util.List;

@Entity
@Table(name = "capture_sessions")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class CaptureSession {
    @Id
    private String sessionId;
    private Long userId;
    private Long startTime;
    private Long endTime;
    private String interfaceName;
    private String interfaceType;
    private String ssid;
    private String localIp;
    private String gateway;
    private String dns;
    private String status;

    @OneToMany(mappedBy = "session", cascade = CascadeType.ALL)
    private List<Packet> packets;
}
