import time
import uuid
import logging
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas
from app.google_auth import validate_google_token, validate_email_domain
from app.auth import generate_jwt_token
from app.logger import setup_logging, log_auth_event, log_database_operation, log_request_info, log_response_info

# Setup logging
logger = setup_logging(__name__)

# Initialize DB
Base.metadata.create_all(bind=engine)
logger.info("✓ Database initialized")

app = FastAPI(title="PACKETIVEX PRODUCTION BACKEND")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✓ CORS middleware configured")

# --- GOOGLE AUTHENTICATION ---

@app.post("/api/auth/google/login", response_model=schemas.AuthResponse)
def google_login(request: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Google OAuth login endpoint.
    Validates Google ID token and verifies email domain is cutmap.ac.in
    
    Args:
        request: GoogleAuthRequest with 'token' field
        db: Database session
        
    Returns:
        AuthResponse with JWT token and user info
    """
    log_request_info(logger, "/api/auth/google/login", "POST", token_length=len(request.token))
    
    try:
        # Validate Google token
        logger.debug("Validating Google ID token...")
        user_info = validate_google_token(request.token)
        
        if not user_info:
            logger.warning("Google token validation failed")
            log_response_info(logger, "/api/auth/google/login", 401, reason="invalid_token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Google token"
            )
        
        email = user_info.get("email")
        logger.debug(f"Token validated for email: {email}")
        
        # Validate domain
        if not validate_email_domain(email):
            logger.warning(f"Domain validation failed for email: {email}")
            log_response_info(logger, "/api/auth/google/login", 403, reason="invalid_domain", email=email)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {email.split('@')[1].split('@')[0] if '@' in email else 'cutmap.ac.in'} domain emails are allowed"
            )
        
        log_auth_event(logger, "domain_validation_success", email)
        
        # Check or create user in database
        log_database_operation(logger, "SELECT", "users", email=email)
        db_user = db.query(models.User).filter(models.User.email == email).first()
        
        if not db_user:
            logger.debug(f"User not found in database. Creating new user: {email}")
            log_database_operation(logger, "INSERT", "users", email=email, name=user_info.get("name"))
            
            db_user = models.User(
                name=user_info.get("name", ""),
                email=email,
                hashed_password="google_oauth",  # Mark as Google OAuth user
                is_active=True
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"✓ New user created via Google Auth: {email}")
            log_auth_event(logger, "user_created", email, method="google")
        else:
            logger.debug(f"User found in database: {email}")
            log_auth_event(logger, "user_found", email)
        
        # Generate JWT token
        jwt_token = generate_jwt_token(email)
        logger.debug(f"JWT token generated for user: {email}")
        
        log_response_info(logger, "/api/auth/google/login", 200, email=email, user_id=db_user.id)
        logger.info(f"✓ Google login successful for: {email}")
        
        return schemas.AuthResponse(
            token=jwt_token,
            userId=str(db_user.id),
            name=db_user.name,
            email=email,
            authMethod="google"
        )
        
    except HTTPException as e:
        logger.error(f"HTTP Exception in Google login: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Google login: {type(e).__name__} - {str(e)}")
        log_response_info(logger, "/api/auth/google/login", 500, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


# --- LEGACY EMAIL/PASSWORD AUTHENTICATION (DEPRECATED) ---

@app.post("/api/auth/register", response_model=schemas.AuthResponse, deprecated=True)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Deprecated: Use Google OAuth instead"""
    logger.warning("Deprecated endpoint called: /api/auth/register - Use Google OAuth instead")
    db_user = models.User(name=user.name, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    return schemas.AuthResponse(
        userId=str(db_user.id),
        name=db_user.name,
        email=db_user.email,
        token="mock-jwt-token",
        authMethod="email"
    )

@app.post("/api/auth/login", response_model=schemas.AuthResponse, deprecated=True)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Deprecated: Use Google OAuth instead"""
    logger.warning("Deprecated endpoint called: /api/auth/login - Use Google OAuth instead")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or db_user.hashed_password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return schemas.AuthResponse(
        userId=str(db_user.id),
        name=db_user.name,
        email=db_user.email,
        token="prod-jwt-token-xyz",
        authMethod="email"
    )

# --- CAPTURE SESSIONS ---

@app.post("/api/capture/start", response_model=schemas.CaptureResponse)
def start_capture(req: schemas.CaptureStartRequest, db: Session = Depends(get_db)):
    log_request_info(logger, "/api/capture/start", "POST", interface=req.interfaceName, ssid=req.ssid)
    
    try:
        sid = str(uuid.uuid4())
        log_database_operation(logger, "INSERT", "capture_sessions", session_id=sid)
        
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
        
        logger.info(f"✓ Capture session started: {sid}")
        log_response_info(logger, "/api/capture/start", 200, session_id=sid)
        
        return schemas.CaptureResponse(sessionId=sid, status="SUCCESS")
    except Exception as e:
        logger.error(f"Error starting capture session: {str(e)}")
        log_response_info(logger, "/api/capture/start", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/capture/end")
def end_capture(req: dict, db: Session = Depends(get_db)):
    sid = req.get("sessionId")
    log_request_info(logger, "/api/capture/end", "POST", session_id=sid)
    
    try:
        log_database_operation(logger, "SELECT", "capture_sessions", session_id=sid)
        session = db.query(models.CaptureSession).filter(models.CaptureSession.session_id == sid).first()
        
        if session:
            session.end_time = int(time.time() * 1000)
            session.status = "COMPLETED"
            db.commit()
            logger.info(f"✓ Capture session ended: {sid}")
            log_database_operation(logger, "UPDATE", "capture_sessions", session_id=sid, status="COMPLETED")
        else:
            logger.warning(f"Session not found: {sid}")
        
        log_response_info(logger, "/api/capture/end", 200, session_id=sid)
        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Error ending capture session: {str(e)}")
        log_response_info(logger, "/api/capture/end", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# --- PACKETS ---

@app.post("/api/packets")
def upload_packet(packet: schemas.PacketCreate, db: Session = Depends(get_db)):
    log_request_info(logger, "/api/packets", "POST", app=packet.appName, protocol=packet.protocol)
    
    try:
        log_database_operation(logger, "INSERT", "packets", session_id=packet.sessionId, app=packet.appName)
        
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
        log_database_operation(logger, "SELECT", "applications", package_name=packet.appPackage)
        app_stat = db.query(models.Application).filter(models.Application.package_name == packet.appPackage).first()
        
        if not app_stat:
            logger.debug(f"Creating new application entry: {packet.appName}")
            log_database_operation(logger, "INSERT", "applications", app_name=packet.appName, package=packet.appPackage)
            app_stat = models.Application(name=packet.appName, package_name=packet.appPackage)
            db.add(app_stat)
        
        app_stat.total_bytes += packet.length
        db.commit()
        
        log_response_info(logger, "/api/packets", 200, app=packet.appName, bytes=packet.length)
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Error uploading packet: {str(e)}")
        log_response_info(logger, "/api/packets", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# --- PCAP UPLOAD ---

@app.post("/api/pcap/upload")
async def upload_pcap(file: UploadFile = File(...), notes: str = Form(""), db: Session = Depends(get_db)):
    log_request_info(logger, "/api/pcap/upload", "POST", filename=file.filename, notes_length=len(notes))
    
    try:
        content = await file.read()
        logger.debug(f"PCAP file read: {file.filename} ({len(content)} bytes)")
        
        log_database_operation(logger, "INSERT", "uploaded_pcap_files", filename=file.filename, size=len(content))
        
        db_file = models.UploadedPcapFile(
            file_name=file.filename,
            file_size=len(content),
            upload_time=int(time.time() * 1000),
            notes=notes
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        logger.info(f"✓ PCAP file uploaded: {file.filename} (ID: {db_file.id})")
        log_response_info(logger, "/api/pcap/upload", 200, file_id=db_file.id, size=len(content))
        
        return {"status": "SUCCESS", "id": db_file.id}
    except Exception as e:
        logger.error(f"Error uploading PCAP file: {str(e)}")
        log_response_info(logger, "/api/pcap/upload", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# --- DASHBOARD ---

@app.get("/api/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    log_request_info(logger, "/api/dashboard", "GET")
    
    try:
        total_packets = db.query(models.Packet).count()
        total_bytes = db.query(func.sum(models.Application.total_bytes)).scalar() or 0
        total_alarms = db.query(models.Alert).count()
        
        logger.debug(f"Dashboard stats: packets={total_packets}, bytes={total_bytes}, alarms={total_alarms}")
        log_response_info(logger, "/api/dashboard", 200, packets=total_packets, bytes=total_bytes)
        
        return schemas.DashboardResponse(
            totalPackets=total_packets,
            totalBytes=total_bytes,
            activeConnections=12,
            openSockets=8,
            totalAlarms=total_alarms
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        log_response_info(logger, "/api/dashboard", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard", response_model=schemas.AnalyticsDashboardResponse)
def get_analytics(db: Session = Depends(get_db)):
    log_request_info(logger, "/api/analytics/dashboard", "GET")
    
    try:
        log_response_info(logger, "/api/analytics/dashboard", 200)
        return schemas.AnalyticsDashboardResponse(
            protocolDistribution=[],
            topApps=[],
            timelinePoints=[],
            highestConsumer="WhatsApp"
        )
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        log_response_info(logger, "/api/analytics/dashboard", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/applications", response_model=List[schemas.AppTrafficSummary])
def get_apps(db: Session = Depends(get_db)):
    log_request_info(logger, "/api/analytics/applications", "GET")
    
    try:
        log_database_operation(logger, "SELECT", "applications", order_by="total_bytes")
        apps = db.query(models.Application).order_by(models.Application.total_bytes.desc()).all()
        
        logger.debug(f"Retrieved {len(apps)} applications")
        log_response_info(logger, "/api/analytics/applications", 200, count=len(apps))
        
        return [schemas.AppTrafficSummary(
            appName=a.name,
            appPackage=a.package_name,
            packetCount=0,
            bytesTransferred=a.total_bytes,
            percentage=0.0
        ) for a in apps]
    except Exception as e:
        logger.error(f"Error fetching applications: {str(e)}")
        log_response_info(logger, "/api/analytics/applications", 500, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/ips")
def get_ips(db: Session = Depends(get_db)):
    log_request_info(logger, "/api/analytics/ips", "GET")
    log_response_info(logger, "/api/analytics/ips", 200)
    return []
