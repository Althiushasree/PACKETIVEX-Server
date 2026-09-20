from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, ForeignKey, Index, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128))
    email = Column(String(128), unique=True, index=True)
    hashed_password = Column(String(256))
    is_active = Column(Boolean, default=True)


class CaptureSession(Base):
    __tablename__ = "capture_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(BigInteger, nullable=False)
    end_time = Column(BigInteger, nullable=True)
    interface_name = Column(String(64))
    interface_type = Column(String(32))
    ssid = Column(String(128))
    local_ip = Column(String(64))
    gateway = Column(String(64))
    dns = Column(String(256))
    status = Column(String(32), default="ACTIVE")

    packets = relationship("Packet", back_populates="session")


class Packet(Base):
    __tablename__ = "packets"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("capture_sessions.session_id"), index=True)
    timestamp = Column(BigInteger, index=True)
    source_ip = Column(String(64))
    dest_ip = Column(String(64))
    source_port = Column(Integer)
    dest_port = Column(Integer)
    protocol = Column(String(32))
    length = Column(Integer)
    app_name = Column(String(128))
    package_name = Column(String(128))
    hostname = Column(String(256))
    http_method = Column(String(16))
    url = Column(String(512))
    tls_sni = Column(String(256))
    payload = Column(LargeBinary, nullable=True)

    session = relationship("CaptureSession", back_populates="packets")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    package_name = Column(String(128), unique=True)
    total_bytes = Column(BigInteger, default=0)


class IpStatistic(Base):
    __tablename__ = "ip_statistics"
    ip_address = Column(String(64), primary_key=True)
    hostname = Column(String(256))
    total_bytes = Column(BigInteger, default=0)


class ProtocolStatistic(Base):
    __tablename__ = "protocol_statistics"
    protocol = Column(String(32), primary_key=True)
    packet_count = Column(BigInteger, default=0)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String(64), primary_key=True)
    title = Column(String(128))
    message = Column(String(512))
    severity = Column(String(32))
    timestamp = Column(BigInteger)


class UploadedPcapFile(Base):
    __tablename__ = "uploaded_pcap_files"
    id = Column(Integer, primary_key=True)
    file_name = Column(String(256))
    file_size = Column(BigInteger)
    upload_time = Column(BigInteger)
    notes = Column(String(512))
