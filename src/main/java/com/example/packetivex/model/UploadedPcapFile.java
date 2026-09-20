package com.example.packetivex.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "uploaded_pcap_files")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class UploadedPcapFile {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String fileName;
    private Long fileSize;
    private Long uploadTime;
    private String notes;
}
