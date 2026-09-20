package com.example.packetivex.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "packets")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class Packet {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "session_id")
    private CaptureSession session;
    
    private Long timestamp;
    private String sourceIp;
    private String destIp;
    private Integer sourcePort;
    private Integer destPort;
    private String protocol;
    private Integer length;
    private String appName;
    private String packageName;
    private String hostname;
    private String httpMethod;
    private String url;
    private String tlsSni;
    
    @Lob
    private byte[] payload;
}
