package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class ProtocolDistribution {
    private String protocol;
    private Integer count;
    private Long bytes;
    private Float percentage;
}
