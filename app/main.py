import time
import uuid
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PACKETIVEX PRODUCTION BACKEND")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION ---

@app.post("/api/auth/register", response_model=schemas.AuthResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email, hashed_password=user.password) # In prod use Bcrypt
    db.add(db_user)
    db.commit()
    return schemas.AuthResponse(userId=str(db_user.id), name=db_user.name, email=db_user.email, token="mock-jwt-token")

@app.post("/api/auth/login", response_model=schemas.AuthResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or db_user.hashed_password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return schemas.AuthResponse(userId=str(db_user.id), name=db_user.name, email=db_user.email, token="prod-jwt-token-xyz")

# --- CAPTURE SESSIONS ---

@app.post("/api/capture/start", response_model=schemas.CaptureResponse)
def start_capture(req: schemas.CaptureStartRequest, db: Session = Depends(get_db)):
    sid = str(uuid.uuid4())
    session = models.CaptureSession(
        session_id=sid,
        start_time=int(time.time() * 1000),
        interface_name=req.interfaceName,
        interface_type=req.interfaceType,
        ssid=req.ssid,
        local_ip=req.localIpv4,
        gateway=req.gateway,
        dns=req.dns
    )
    db.add(session)
    db.commit()
    return schemas.CaptureResponse(sessionId=sid, status="SUCCESS")

@app.post("/api/capture/end")
def end_capture(req: dict, db: Session = Depends(get_db)):
    sid = req.get("sessionId")
    session = db.query(models.CaptureSession).filter(models.CaptureSession.session_id == sid).first()
    if session:
        session.end_time = int(time.time() * 1000)
        session.status = "COMPLETED"
        db.commit()
    return {"status": "SUCCESS"}

# --- PACKETS ---

@app.post("/api/packets")
def upload_packet(packet: schemas.PacketCreate, db: Session = Depends(get_db)):
    db_packet = models.Packet(
        session_id=packet.sessionId,
        timestamp=packet.timestamp,
        source_ip=packet.sourceIp,
        dest_ip=packet.destIp,
        source_port=packet.sourcePort,
        dest_port=packet.destPort,
        protocol=packet.protocol,
        length=packet.length,
        app_name=packet.appName,
        package_name=packet.appPackage,
        hostname=packet.hostname,
        http_method=packet.httpMethod,
        url=packet.url,
        tls_sni=packet.tlsSni
    )
    db.add(db_packet)

    # Update stats
    app_stat = db.query(models.Application).filter(models.Application.package_name == packet.appPackage).first()
    if not app_stat:
        app_stat = models.Application(name=packet.appName, package_name=packet.appPackage)
        db.add(app_stat)
    app_stat.total_bytes += packet.length

    db.commit()
    return {"status": "OK"}

# --- PCAP UPLOAD ---

@app.post("/api/pcap/upload")
async def upload_pcap(file: UploadFile = File(...), notes: str = Form(""), db: Session = Depends(get_db)):
    content = await file.read()
    db_file = models.UploadedPcapFile(
        file_name=file.filename,
        file_size=len(content),
        upload_time=int(time.time() * 1000),
        notes=notes
    )
    db.add(db_file)
    db.commit()
    return {"status": "SUCCESS", "id": db_file.id}

# --- DASHBOARD ---

@app.get("/api/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    return schemas.DashboardResponse(
        totalPackets=db.query(models.Packet).count(),
        totalBytes=db.query(models.Application).with_entities(func.sum(models.Application.total_bytes)).scalar() or 0,
        activeConnections=12, # Real logic would query active sessions
        openSockets=8,
        totalAlarms=db.query(models.Alert).count()
    )

@app.get("/api/analytics/dashboard", response_model=schemas.AnalyticsDashboardResponse)
def get_analytics(db: Session = Depends(get_db)):
    return schemas.AnalyticsDashboardResponse(
        protocolDistribution=[], # Query from protocol_statistics
        topApps=[], # Query from applications
        timelinePoints=[],
        highestConsumer="WhatsApp"
    )

@app.get("/api/analytics/applications", response_model=List[schemas.AppTrafficSummary])
def get_apps(db: Session = Depends(get_db)):
    apps = db.query(models.Application).order_by(models.Application.total_bytes.desc()).all()
    return [schemas.AppTrafficSummary(appName=a.name, appPackage=a.package_name, packetCount=0, bytesTransferred=a.total_bytes, percentage=0.0) for a in apps]

@app.get("/api/analytics/ips")
def get_ips(db: Session = Depends(get_db)):
    return []
