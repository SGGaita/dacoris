from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class AccountType(str, enum.Enum):
    ORCID = "orcid"
    GLOBAL_ADMIN = "global_admin"
    INSTITUTION_ADMIN = "institution_admin"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"

class ResearchRole(str, enum.Enum):
    PRINCIPAL_INVESTIGATOR = "principal_investigator"
    GRANT_OFFICER = "grant_officer"
    ETHICS_REVIEWER = "ethics_reviewer"
    DATA_STEWARD = "data_steward"
    DATA_ENGINEER = "data_engineer"
    INSTITUTIONAL_LEAD = "institutional_lead"
    SYSTEM_ADMIN = "system_admin"

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', Enum(ResearchRole), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by', Integer, ForeignKey('users.id'), nullable=True)
)

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=False, unique=True)
    verified_domains = Column(Text, nullable=True)
    orcid_client_id = Column(String, nullable=True)
    orcid_client_secret = Column(String, nullable=True)
    orcid_redirect_uri = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    users = relationship("User", back_populates="institution", foreign_keys="User.primary_institution_id")
    orcid_profiles = relationship("OrcidProfile", back_populates="institution")

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', 'primary_institution_id', name='uix_email_institution'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.ORCID)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    orcid_id = Column(String, unique=True, index=True, nullable=True)
    orcid_access_token = Column(String, nullable=True)
    orcid_refresh_token = Column(String, nullable=True)
    orcid_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    orcid_profile_last_sync = Column(DateTime(timezone=True), nullable=True)
    
    primary_institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=True, index=True)
    is_global_admin = Column(Boolean, default=False, nullable=False)
    is_institution_admin = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    institution = relationship("Institution", back_populates="users", foreign_keys=[primary_institution_id])
    orcid_profile = relationship("OrcidProfile", back_populates="user", uselist=False)

class OrcidProfile(Base):
    __tablename__ = "orcid_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=True)
    
    orcid_id = Column(String, nullable=False, index=True)
    given_names = Column(String, nullable=True)
    family_name = Column(String, nullable=True)
    biography = Column(Text, nullable=True)
    
    affiliations = Column(Text, nullable=True)
    works = Column(Text, nullable=True)
    funding = Column(Text, nullable=True)
    
    visibility_status = Column(String, nullable=True)
    is_public = Column(Boolean, default=False)
    
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="orcid_profile")
    institution = relationship("Institution", back_populates="orcid_profiles")
