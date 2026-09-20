package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class AppTrafficSummary {
    private String appName;
    private String appPackage;
    private Integer packetCount;
    private Long bytesTransferred;
    private Float percentage;
}
