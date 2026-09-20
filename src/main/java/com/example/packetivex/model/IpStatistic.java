package com.example.packetivex.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "ip_statistics")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class IpStatistic {
    @Id
    private String ipAddress;
    private String hostname;
    private Long totalBytes;
}
