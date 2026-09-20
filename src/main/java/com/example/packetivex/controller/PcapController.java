package com.example.packetivex.controller;

import com.example.packetivex.model.UploadedPcapFile;
import com.example.packetivex.repository.UploadedPcapFileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.util.Map;

@RestController
@RequestMapping("/api/pcap")
@RequiredArgsConstructor
public class PcapController {
    private final UploadedPcapFileRepository pcapFileRepository;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadPcap(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "notes", required = false) String notes) {
        
        UploadedPcapFile pcap = new UploadedPcapFile();
        pcap.setFileName(file.getOriginalFilename());
        pcap.setFileSize(file.getSize());
        pcap.setUploadTime(System.currentTimeMillis());
        pcap.setNotes(notes);
        pcapFileRepository.save(pcap);
        
        return ResponseEntity.ok(Map.of("status", "SUCCESS", "id", pcap.getId()));
    }
}
