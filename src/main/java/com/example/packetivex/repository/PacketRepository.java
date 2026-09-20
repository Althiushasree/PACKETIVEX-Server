package com.example.packetivex.repository;

import com.example.packetivex.model.Packet;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PacketRepository extends JpaRepository<Packet, Long> {
}
