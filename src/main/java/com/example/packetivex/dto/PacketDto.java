package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class PacketDto {
    private String sessionId;
    private Long timestamp;
    private String sourceIp;
    private String destIp;
    private Integer sourcePort;
    private Integer destPort;
    private String protocol;
    private Integer length;
    private String appName;
    private String appPackage;
    private String hostname;
    private String httpMethod;
    private String url;
    private String tlsSni;
    private String payloadHex;
}
