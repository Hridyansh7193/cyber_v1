from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ScanSessionModel(Base):
    __tablename__ = 'scan_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, unique=True, index=True)
    target_domain = Column(String, nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class TargetModel(Base):
    __tablename__ = 'targets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String, nullable=False, unique=True, index=True)
    scope_type = Column(String, nullable=True)
    program_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class SubdomainModel(Base):
    __tablename__ = 'subdomains'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    subdomain = Column(String, nullable=False, index=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class AliveHostModel(Base):
    __tablename__ = 'alive_hosts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    status_code = Column(Integer, nullable=True)
    title = Column(String, nullable=True)
    tech_stack = Column(String, nullable=True)
    response_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class UrlModel(Base):
    __tablename__ = 'urls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class ParameterModel(Base):
    __tablename__ = 'parameters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    url = Column(String, nullable=False)
    parameter = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class JSFileModel(Base):
    __tablename__ = 'js_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class SecretModel(Base):
    __tablename__ = 'secrets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    value = Column(String, nullable=False)
    source = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class APIEndpointModel(Base):
    __tablename__ = 'api_endpoints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class FindingModel(Base):
    __tablename__ = 'findings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    title = Column(String, nullable=False)
    severity = Column(String, nullable=False, index=True)
    confidence = Column(String, nullable=False)
    description = Column(String, nullable=True)
    evidence = Column(String, nullable=True)
    poc = Column(String, nullable=True)
    plugin = Column(String, nullable=True)
    tool_version = Column(String, nullable=True)
    target = Column(String, nullable=True)
    url = Column(String, nullable=True)
    template_id = Column(String, nullable=True)
    category = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    recommendation = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    command = Column(String, nullable=True)
    replay_command = Column(String, nullable=True)
    parser = Column(String, nullable=True)
    metadata_json = Column(String, nullable=True)
    source_tool = Column(String, nullable=True)
    references_json = Column(String, nullable=True)
    status = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class ReportModel(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    report_path = Column(String, nullable=False)
    report_format = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class TaskHistoryModel(Base):
    __tablename__ = 'task_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    attempts = Column(Integer, default=0)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

class LogModel(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('scan_sessions.session_id'), nullable=False, index=True)
    component = Column(String, nullable=False, index=True)
    level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
