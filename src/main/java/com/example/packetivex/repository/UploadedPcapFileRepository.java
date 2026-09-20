package com.example.packetivex.repository;

import com.example.packetivex.model.UploadedPcapFile;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UploadedPcapFileRepository extends JpaRepository<UploadedPcapFile, Long> {
}
