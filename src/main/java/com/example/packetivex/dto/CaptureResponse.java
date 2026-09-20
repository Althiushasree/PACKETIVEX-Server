package com.example.packetivex.dto;

import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class CaptureResponse {
    private String sessionId;
    private String status;
}
