package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class TimelinePoint {
    private String label;
    private Long timestamp;
    private Long totalBytes;
    private Long downloadBytes;
    private Long uploadBytes;
    private Integer packetCount;
}
