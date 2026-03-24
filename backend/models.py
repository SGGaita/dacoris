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

class PrimaryAccountType(str, enum.Enum):
    RESEARCHER = "researcher"
    GRANT_MANAGER = "grant_manager"
    FINANCE_OFFICER = "finance_officer"
    ETHICS_COMMITTEE_MEMBER = "ethics_committee_member"
    DATA_STEWARD = "data_steward"
    DATA_ENGINEER = "data_engineer"
    INSTITUTIONAL_LEADERSHIP = "institutional_leadership"
    EXTERNAL_REVIEWER = "external_reviewer"
    GUEST_COLLABORATOR = "guest_collaborator"
    EXTERNAL_FUNDER = "external_funder"

class ResearchRole(str, enum.Enum):
    RESEARCHER = "researcher"
    PRINCIPAL_INVESTIGATOR = "principal_investigator"
    CO_INVESTIGATOR = "co_investigator"
    GRANT_OFFICER = "grant_officer"
    RESEARCH_ADMIN = "research_admin"
    FINANCE_OFFICER = "finance_officer"
    ETHICS_REVIEWER = "ethics_reviewer"
    ETHICS_CHAIR = "ethics_chair"
    DATA_STEWARD = "data_steward"
    DATA_ENGINEER = "data_engineer"
    INSTITUTIONAL_LEAD = "institutional_lead"
    SYSTEM_ADMIN = "system_admin"
    EXTERNAL_REVIEWER = "external_reviewer"
    GUEST_COLLABORATOR = "guest_collaborator"
    EXTERNAL_FUNDER = "external_funder"
    APPLICANT = "applicant"

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
    
    primary_account_type = Column(Enum(PrimaryAccountType), nullable=True)
    department = Column(String(200), nullable=True)
    job_title = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    expertise_keywords = Column(Text, nullable=True)
    
    is_guest = Column(Boolean, default=False, nullable=False)
    access_expires_at = Column(DateTime(timezone=True), nullable=True)
    invited_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    invitation_context = Column(Text, nullable=True)
    
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


# ============================================================
# PROTOTYPE MODELS - APPEND ONLY, DO NOT MODIFY ABOVE
# ============================================================

# ─── SHARED ENUMS ────────────────────────────────────────────────────────────

class ProposalStatus(str, enum.Enum):
    DRAFT = "draft"
    INTERNAL_REVIEW = "internal_review"
    RETURNED = "returned"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    AWARDED = "awarded"
    DECLINED = "declined"

class AwardStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    TERMINATED = "terminated"

class ProjectStatus(str, enum.Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"

class EthicsStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    APPROVED_WITH_MODS = "approved_with_modifications"
    REJECTED = "rejected"
    DEFERRED = "deferred"

class ReviewStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"

class QAStatus(str, enum.Enum):
    STAGED = "staged"
    PASSED = "passed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


# ─── GRANT MODULE MODELS ─────────────────────────────────────────────────────

class GrantOpportunity(Base):
    __tablename__ = "grant_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    title = Column(String(500), nullable=False)
    sponsor = Column(String(300))
    description = Column(Text)
    category = Column(String(200))
    geography = Column(String(200))
    applicant_type = Column(String(200))
    funding_type = Column(String(100))
    amount_min = Column(Integer)
    amount_max = Column(Integer)
    currency = Column(String(10), default="KES")
    open_date = Column(DateTime(timezone=True))
    deadline = Column(DateTime(timezone=True))
    source_system = Column(String(100), default="internal")
    source_id = Column(String(200))
    status = Column(String(50), default="open")
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    proposals = relationship("Proposal", back_populates="opportunity")
    created_by = relationship("User", foreign_keys=[created_by_id])


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("grant_opportunities.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    lead_pi_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT)
    submitted_at = Column(DateTime(timezone=True))
    current_version = Column(Integer, default=1)
    internal_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    opportunity = relationship("GrantOpportunity", back_populates="proposals")
    lead_pi = relationship("User", foreign_keys=[lead_pi_id])
    sections = relationship("ProposalSection", back_populates="proposal",
                            cascade="all, delete-orphan")
    documents = relationship("ProposalDocument", back_populates="proposal",
                             cascade="all, delete-orphan")
    collaborators = relationship("ProposalCollaborator", back_populates="proposal",
                                 cascade="all, delete-orphan")
    reviews = relationship("ProposalReview", back_populates="proposal",
                           cascade="all, delete-orphan")
    award = relationship("Award", back_populates="proposal", uselist=False)


class ProposalSection(Base):
    __tablename__ = "proposal_sections"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    section_type = Column(String(100), nullable=False)
    title = Column(String(300), nullable=False)
    content_html = Column(Text, default="")
    word_count = Column(Integer, default=0)
    version = Column(Integer, default=1)
    last_edited_by_id = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    proposal = relationship("Proposal", back_populates="sections")
    last_edited_by = relationship("User", foreign_keys=[last_edited_by_id])


class ProposalDocument(Base):
    __tablename__ = "proposal_documents"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    document_type = Column(String(100))
    original_filename = Column(String(500))
    stored_filename = Column(String(500))
    file_size_bytes = Column(Integer)
    mime_type = Column(String(200))
    uploaded_by_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    proposal = relationship("Proposal", back_populates="documents")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])


class ProposalCollaborator(Base):
    __tablename__ = "proposal_collaborators"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(100), default="co_investigator")
    can_edit = Column(Boolean, default=True)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())

    proposal = relationship("Proposal", back_populates="collaborators")
    user = relationship("User", foreign_keys=[user_id])


class ProposalReview(Base):
    __tablename__ = "proposal_reviews"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.ASSIGNED)
    has_coi = Column(Boolean, default=False)
    coi_reason = Column(Text)
    scores = Column(Text, default="{}")
    overall_score = Column(Integer)
    recommendation = Column(String(50))
    narrative_feedback = Column(Text)
    submitted_at = Column(DateTime(timezone=True))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    proposal = relationship("Proposal", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])


class Award(Base):
    __tablename__ = "awards"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False, unique=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    award_number = Column(String(100), unique=True)
    funder_name = Column(String(300))
    total_amount = Column(Integer, nullable=False)
    currency = Column(String(10), default="KES")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(Enum(AwardStatus), default=AwardStatus.ACTIVE)
    conditions = Column(Text)
    issued_by_id = Column(Integer, ForeignKey("users.id"))
    issued_at = Column(DateTime(timezone=True), server_default=func.now())

    proposal = relationship("Proposal", back_populates="award")
    issued_by = relationship("User", foreign_keys=[issued_by_id])
    budget_lines = relationship("BudgetLine", back_populates="award",
                                cascade="all, delete-orphan")
    research_project = relationship("ResearchProject", back_populates="award",
                                    uselist=False)


class BudgetLine(Base):
    __tablename__ = "budget_lines"

    id = Column(Integer, primary_key=True, index=True)
    award_id = Column(Integer, ForeignKey("awards.id"), nullable=False)
    category = Column(String(200), nullable=False)
    description = Column(String(500))
    amount = Column(Integer, nullable=False)
    spent_to_date = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    award = relationship("Award", back_populates="budget_lines")


# ─── RESEARCH MODULE MODELS ───────────────────────────────────────────────────

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    award_id = Column(Integer, ForeignKey("awards.id"), nullable=True)
    pi_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    project_type = Column(String(100), default="funded")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PROPOSED)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    involves_human_subjects = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    award = relationship("Award", back_populates="research_project")
    pi = relationship("User", foreign_keys=[pi_id])
    ethics_applications = relationship("EthicsApplication",
                                       back_populates="project",
                                       cascade="all, delete-orphan")
    capture_forms = relationship("CaptureForm", back_populates="project")


class EthicsApplication(Base):
    __tablename__ = "ethics_applications"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    application_type = Column(String(100), default="full_review")
    status = Column(Enum(EthicsStatus), default=EthicsStatus.DRAFT)
    title = Column(String(500))
    lay_summary = Column(Text)
    methodology = Column(Text)
    risk_assessment = Column(Text)
    data_handling = Column(Text)
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    submitted_at = Column(DateTime(timezone=True))
    decision_notes = Column(Text)
    approved_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("ResearchProject", back_populates="ethics_applications")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])


# ─── DATA MODULE A MODELS ────────────────────────────────────────────────────

class CaptureForm(Base):
    __tablename__ = "capture_forms"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    form_schema = Column(Text, default='{"fields": []}')
    source_system = Column(String(50), default="internal")
    external_form_id = Column(String(200))
    external_endpoint = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("ResearchProject", back_populates="capture_forms")
    created_by = relationship("User", foreign_keys=[created_by_id])
    submissions = relationship("FormSubmission", back_populates="form",
                               cascade="all, delete-orphan")


class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("capture_forms.id"), nullable=False)
    data = Column(Text, nullable=False)
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_system = Column(String(50), default="internal")
    external_submission_id = Column(String(200))
    qa_status = Column(Enum(QAStatus), default=QAStatus.STAGED)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    form = relationship("CaptureForm", back_populates="submissions")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])


# ─── CROSS-CUTTING: NOTIFICATIONS ────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    message = Column(Text)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
