package com.example.packetivex.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "protocol_statistics")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class ProtocolStatistic {
    @Id
    private String protocol;
    private Long packetCount;
}
