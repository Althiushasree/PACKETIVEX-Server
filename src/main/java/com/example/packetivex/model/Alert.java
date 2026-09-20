package com.example.packetivex.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "alerts")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class Alert {
    @Id
    private String id;
    private String title;
    private String message;
    private String severity;
    private Long timestamp;
}
