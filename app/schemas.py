from pydantic import BaseModel
from typing import List, Optional


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth token verification"""
    token: str
    

class AuthResponse(BaseModel):
    token: Optional[str]
    userId: Optional[str]
    name: Optional[str]
    email: Optional[str]
    message: Optional[str]
    authMethod: Optional[str] = "google"  # Can be 'google' or 'email'


class CaptureStartRequest(BaseModel):
    action: str
    interfaceName: Optional[str]
    interfaceType: Optional[str]
    ssid: Optional[str]
    localIpv4: Optional[str]
    gateway: Optional[str]
    dns: Optional[str]


class CaptureResponse(BaseModel):
    sessionId: str
    status: str


class PacketCreate(BaseModel):
    sessionId: str
    timestamp: int
    sourceIp: str
    destIp: str
    sourcePort: int
    destPort: int
    protocol: str
    length: int
    appName: str
    appPackage: str
    hostname: str
    httpMethod: Optional[str]
    url: Optional[str]
    tlsSni: Optional[str]
    payloadHex: Optional[str]


class NetworkStats(BaseModel):
    totalPacketsCaptured: int
    totalBytesCaptured: int
    downloadSpeedMbps: float
    uploadSpeedMbps: float
    durationSeconds: int
    activeConnectionsCount: int
    openSocketsCount: int
    totalAlarmsCount: int


class DashboardResponse(BaseModel):
    totalPackets: int
    totalBytes: int
    activeConnections: int
    openSockets: int
    totalAlarms: int


class ProtocolDistribution(BaseModel):
    protocol: str
    count: int
    bytes: int
    percentage: float


class AppTrafficSummary(BaseModel):
    appName: str
    appPackage: str
    packetCount: int
    bytesTransferred: int
    percentage: float


class IpUsageSummary(BaseModel):
    ip: str
    hostname: str
    bytes: int
    packetCount: int
    percentage: float


class TimelinePoint(BaseModel):
    label: str
    timestamp: int
    totalBytes: int
    downloadBytes: int
    uploadBytes: int
    packetCount: int


class AnalyticsDashboardResponse(BaseModel):
    protocolDistribution: List[ProtocolDistribution]
    topApps: List[AppTrafficSummary]
    timelinePoints: List[TimelinePoint]
    highestConsumer: str
