package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class CaptureStartRequest {
    private String action;
    private String interfaceName;
    private String interfaceType;
    private String ssid;
    private String localIpv4;
    private String gateway;
    private String dns;
}
