# DACORIS – Prototype Implementation Guide
**Target:** Working prototype in 2 weeks from commencement  
**Stack:** FastAPI · PostgreSQL · SQLAlchemy (async) · Alembic · Next.js 15 · MUI · Zustand  
**Foundation:** IAM layer already implemented — build on top, do not modify existing auth files

---

## Table of Contents

1. [Prototype Scope](#1-prototype-scope)
2. [Project Structure After Prototype](#2-project-structure-after-prototype)
3. [Environment Setup](#3-environment-setup)
4. [Week 1 — Backend: Database, Models & Core APIs](#4-week-1--backend-database-models--core-apis)
   - Day 1: Dependencies & Alembic Setup
   - Day 2: Grant Module Models
   - Day 3: Grant API — Opportunities & Proposals
   - Day 4: Grant API — Workflow, Review & Award
   - Day 5: Research & Data Capture Models + APIs
5. [Week 2 — Frontend: Screens & Integration](#5-week-2--frontend-screens--integration)
   - Day 6: Shared Layout, Navigation & API Client
   - Day 7: Grant — Opportunity & Proposal Screens
   - Day 8: Grant — Review Console & Award Screen
   - Day 9: Research — Project & Ethics Screens
   - Day 10: Data Capture — Form Builder & Submission View
   - Day 11–12: Polish, Seed Data & Demo Prep
6. [Database Migrations Reference](#6-database-migrations-reference)
7. [Seed Data Script](#7-seed-data-script)
8. [API Reference (Prototype Endpoints)](#8-api-reference-prototype-endpoints)
9. [Frontend Routes Map](#9-frontend-routes-map)
10. [Demo Scenario Script](#10-demo-scenario-script)
11. [Known Limitations & V1.0 Deferrals](#11-known-limitations--v10-deferrals)
12. [Prototype Checklist](#12-prototype-checklist)

---

## 1. Prototype Scope

### What the prototype demonstrates

The prototype proves the core DACORIS value proposition end-to-end across three modules with enough fidelity to show stakeholders and collect real feedback. It is **not** production-ready — shortcuts are deliberate and documented.

| Module | Prototype Includes | Prototype Excludes |
|---|---|---|
| **IAM** | ✅ All existing (users, roles, institutions, ORCID, admin dashboards) | MFA, SAML, SCIM |
| **Grant** | ✅ Opportunity CRUD, Proposal with sections, Collaborator invite, Basic review/scoring, Award issuance, Budget setup | Finance ERP sync, Expense reports, CRM, Audit pack export, Disbursement schedules |
| **Research** | ✅ Project registration (manual + award-linked), Researcher profile view, Basic ethics application submission | Ethics committee review workflow, ORCID publication sync, OAI-PMH, Public portal |
| **Data A** | ✅ Form builder (basic), KoBoToolbox connection config, Submission list view, Manual CSV upload | ODK/REDCap/MSForms connectors, QA pipeline automation, Repository/DOI, Analysis workspace |
| **Data B** | ❌ Not in prototype | Entire module deferred to Phase 4 |

### Prototype acceptance criteria

A successful prototype must demonstrate this complete scenario end-to-end:

1. Grant Officer creates a funding opportunity
2. PI creates a proposal with two sections and uploads a document
3. External reviewer scores the proposal
4. Grant Officer issues an award
5. Award automatically creates a Research project
6. PI submits an ethics application linked to the project
7. Data Steward creates a capture form and links it to KoBoToolbox
8. Institution Admin views a dashboard showing all activity

---

## 2. Project Structure After Prototype

```
dacoris/
├── backend/
│   ├── main.py                          # ← ADD: new router imports
│   ├── models.py                        # ← ADD: all new models (append only)
│   ├── auth.py                          # ✅ unchanged
│   ├── database.py                      # ✅ unchanged
│   ├── manage.py                        # ✅ unchanged
│   ├── requirements.txt                 # ← ADD: new dependencies
│   ├── alembic.ini                      # ← NEW
│   ├── alembic/
│   │   ├── env.py                       # ← NEW
│   │   └── versions/
│   │       ├── 001_grant_models.py      # ← NEW
│   │       ├── 002_research_models.py   # ← NEW
│   │       └── 003_data_capture.py      # ← NEW
│   ├── routes/
│   │   ├── auth.py                      # ✅ unchanged
│   │   ├── orcid.py                     # ✅ unchanged
│   │   ├── global_admin.py              # ✅ unchanged
│   │   ├── institution_admin.py         # ✅ unchanged
│   │   ├── onboarding.py               # ✅ unchanged
│   │   ├── grants/                      # ← NEW directory
│   │   │   ├── __init__.py
│   │   │   ├── opportunities.py
│   │   │   ├── proposals.py
│   │   │   ├── reviews.py
│   │   │   └── awards.py
│   │   ├── research/                    # ← NEW directory
│   │   │   ├── __init__.py
│   │   │   ├── projects.py
│   │   │   └── ethics.py
│   │   └── data/                        # ← NEW directory
│   │       ├── __init__.py
│   │       ├── forms.py
│   │       └── submissions.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── orcid_sync.py               # ✅ unchanged
│   │   ├── workflow.py                  # ← NEW: stage transition logic
│   │   ├── notifications.py             # ← NEW: in-app notification helpers
│   │   └── file_upload.py               # ← NEW: file handling
│   └── schemas/                         # ← NEW directory
│       ├── __init__.py
│       ├── grants.py                    # Pydantic request/response models
│       ├── research.py
│       └── data.py
│
└── frontend/
    ├── app/
    │   ├── login/page.js                # ✅ unchanged
    │   ├── onboarding/page.js           # ✅ unchanged
    │   ├── global-admin/page.js         # ✅ unchanged
    │   ├── institution-admin/page.js    # ✅ unchanged
    │   ├── dashboard/page.js            # ← EXTEND: add module tiles
    │   ├── grants/
    │   │   ├── page.js                  # ← NEW: opportunities list
    │   │   ├── new/page.js              # ← NEW: create opportunity
    │   │   ├── [id]/page.js             # ← NEW: opportunity detail
    │   │   └── proposals/
    │   │       ├── new/page.js          # ← NEW: create proposal
    │   │       └── [id]/page.js         # ← NEW: proposal workspace
    │   ├── review/
    │   │   └── [id]/page.js             # ← NEW: review console
    │   ├── awards/
    │   │   └── [id]/page.js             # ← NEW: award detail + budget
    │   ├── research/
    │   │   ├── page.js                  # ← NEW: projects list
    │   │   ├── new/page.js              # ← NEW: register project
    │   │   ├── [id]/page.js             # ← NEW: project workspace
    │   │   └── ethics/
    │   │       └── new/page.js          # ← NEW: ethics application
    │   └── data/
    │       ├── page.js                  # ← NEW: forms list
    │       ├── forms/
    │       │   ├── new/page.js          # ← NEW: form builder
    │       │   └── [id]/page.js         # ← NEW: submissions view
    │       └── upload/page.js           # ← NEW: CSV upload
    ├── components/
    │   ├── layout/
    │   │   ├── AppShell.js              # ← NEW: sidebar + topbar
    │   │   └── ModuleNav.js             # ← NEW: module navigation
    │   ├── grants/
    │   │   ├── ProposalEditor.js        # ← NEW: section editor
    │   │   ├── ScoringRubric.js         # ← NEW: review scoring UI
    │   │   └── BudgetTable.js           # ← NEW: budget line items
    │   ├── research/
    │   │   └── EthicsForm.js            # ← NEW: ethics submission
    │   └── data/
    │       └── FormBuilder.js           # ← NEW: drag-drop form builder
    ├── lib/
    │   ├── api.js                       # ✅ unchanged (extend with new methods)
    │   └── apiModules.js                # ← NEW: module-specific API calls
    └── store/
        ├── authStore.js                 # ✅ unchanged
        └── appStore.js                  # ← NEW: notifications, UI state
```

---

## 3. Environment Setup

### 3.1 New backend dependencies

Add to `backend/requirements.txt`:

```txt
# Existing (keep all)
fastapi
uvicorn
sqlalchemy[asyncio]
asyncpg
python-dotenv
pydantic[email]
python-jose[cryptography]
passlib[bcrypt]
httpx
alembic                    # ← ADD if not present

# New for prototype
python-multipart           # file upload support
aiofiles                   # async file I/O
pillow                     # image handling (for document previews)
python-slugify             # URL-safe slugs for proposals
```

Install:
```bash
cd backend
pip install python-multipart aiofiles python-slugify alembic
pip freeze > requirements.txt
```

### 3.2 New frontend dependencies

```bash
cd frontend
npm install @hello-pangea/dnd   # drag-and-drop for form builder
npm install react-quill          # rich text editor for proposal sections
npm install dayjs                # date formatting
npm install recharts             # charts for dashboard
npm install react-dropzone       # file upload UI
```

### 3.3 Add to `.env` (backend)

```env
# File Storage (local for prototype)
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50

# Notifications (console logging for prototype — no email service needed)
NOTIFICATION_MODE=console

# KoBoToolbox (prototype integration)
KOBO_API_BASE_URL=https://kf.kobotoolbox.org/api/v2
```

### 3.4 Create upload directory

```bash
mkdir -p backend/uploads/documents
mkdir -p backend/uploads/datasets
echo "uploads/" >> backend/.gitignore
```

### 3.5 Initialise Alembic

```bash
cd backend
alembic init alembic
```

Edit `alembic/env.py` — replace the `target_metadata` section:

```python
# alembic/env.py — replace lines around target_metadata
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import DATABASE_URL
from models import Base         # imports ALL models

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("+asyncpg", ""))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 4. Week 1 — Backend: Database, Models & Core APIs

---

### Day 1 — New Models: Append to `backend/models.py`

> **Rule:** Never modify existing model classes. Append all new models below the existing ones.

```python
# ============================================================
# APPEND BELOW EXISTING MODELS IN backend/models.py
# ============================================================
import enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Enum as SAEnum, JSON, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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
    amount_min = Column(Float)
    amount_max = Column(Float)
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
    status = Column(SAEnum(ProposalStatus), default=ProposalStatus.DRAFT)
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
    section_type = Column(String(100), nullable=False)   # executive_summary, problem_statement, etc.
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
    document_type = Column(String(100))   # cv, budget_justification, consent_form, etc.
    original_filename = Column(String(500))
    stored_filename = Column(String(500))
    file_size_bytes = Column(BigInteger)
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
    status = Column(SAEnum(ReviewStatus), default=ReviewStatus.ASSIGNED)
    has_coi = Column(Boolean, default=False)
    coi_reason = Column(Text)
    # Scores: JSON object {criterion: score}
    scores = Column(JSON, default={})
    overall_score = Column(Float)
    recommendation = Column(String(50))   # recommend / do_not_recommend / conditional
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
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="KES")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(SAEnum(AwardStatus), default=AwardStatus.ACTIVE)
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
    amount = Column(Float, nullable=False)
    spent_to_date = Column(Float, default=0.0)
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
    status = Column(SAEnum(ProjectStatus), default=ProjectStatus.PROPOSED)
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
    status = Column(SAEnum(EthicsStatus), default=EthicsStatus.DRAFT)
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
    # XLSForm-compatible schema stored as JSON
    form_schema = Column(JSON, default={"fields": []})
    source_system = Column(String(50), default="internal")
    # For KoBoToolbox: store the remote form UID
    external_form_id = Column(String(200))
    # KoBoToolbox API endpoint for this form's submissions
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
    data = Column(JSON, nullable=False)
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_system = Column(String(50), default="internal")
    # External system's submission ID (for deduplication)
    external_submission_id = Column(String(200))
    qa_status = Column(SAEnum(QAStatus), default=QAStatus.STAGED)
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
    entity_type = Column(String(100))   # proposal, award, project, ethics, form
    entity_id = Column(Integer)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
```

Run migration:
```bash
cd backend
alembic revision --autogenerate -m "add_grant_research_data_models"
alembic upgrade head
```

---

### Day 2 — Services: Workflow, Notifications & File Upload

**`backend/services/workflow.py`**

```python
"""
Prototype workflow service — simplified state machine.
Enforces allowed transitions. For prototype, no complex rule evaluation.
"""
from models import ProposalStatus, AwardStatus, ProjectStatus, EthicsStatus

# Allowed status transitions per entity
PROPOSAL_TRANSITIONS = {
    ProposalStatus.DRAFT: [ProposalStatus.INTERNAL_REVIEW],
    ProposalStatus.INTERNAL_REVIEW: [ProposalStatus.RETURNED, ProposalStatus.SUBMITTED],
    ProposalStatus.RETURNED: [ProposalStatus.DRAFT],
    ProposalStatus.SUBMITTED: [ProposalStatus.UNDER_REVIEW],
    ProposalStatus.UNDER_REVIEW: [ProposalStatus.AWARDED, ProposalStatus.DECLINED],
}

ETHICS_TRANSITIONS = {
    EthicsStatus.DRAFT: [EthicsStatus.SUBMITTED],
    EthicsStatus.SUBMITTED: [EthicsStatus.UNDER_REVIEW],
    EthicsStatus.UNDER_REVIEW: [
        EthicsStatus.APPROVED,
        EthicsStatus.APPROVED_WITH_MODS,
        EthicsStatus.REJECTED,
        EthicsStatus.DEFERRED,
    ],
    EthicsStatus.DEFERRED: [EthicsStatus.SUBMITTED],
}

def can_transition_proposal(current: ProposalStatus, target: ProposalStatus) -> bool:
    allowed = PROPOSAL_TRANSITIONS.get(current, [])
    return target in allowed

def can_transition_ethics(current: EthicsStatus, target: EthicsStatus) -> bool:
    allowed = ETHICS_TRANSITIONS.get(current, [])
    return target in allowed
```

**`backend/services/notifications.py`**

```python
"""
Prototype notification service — stores in-app notifications.
Logs to console (no email in prototype).
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from models import Notification

logger = logging.getLogger("dacoris.notifications")

async def create_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    message: str,
    entity_type: str = None,
    entity_id: int = None,
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(notification)
    await db.commit()
    logger.info(f"[NOTIFY] user={user_id} | {title}")
    return notification
```

**`backend/services/file_upload.py`**

```python
"""
Prototype file upload service — stores files to local disk.
Replace with S3/MinIO in V1.0.
"""
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 50)) * 1024 * 1024

ALLOWED_TYPES = {
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv", "image/jpeg", "image/png",
}

async def save_upload(file: UploadFile, subfolder: str = "documents") -> dict:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {file.content_type} not allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File exceeds {MAX_FILE_SIZE // 1024 // 1024}MB limit")

    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, subfolder, stored_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    async with aiofiles.open(path, "wb") as f:
        await f.write(content)

    return {
        "original_filename": file.filename,
        "stored_filename": stored_name,
        "file_size_bytes": len(content),
        "mime_type": file.content_type,
        "path": path,
    }

def get_file_path(stored_filename: str, subfolder: str = "documents") -> str:
    return os.path.join(UPLOAD_DIR, subfolder, stored_filename)
```

---

### Day 3 — Grant APIs: Opportunities & Proposals

**`backend/routes/grants/opportunities.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import GrantOpportunity, User
from auth import require_roles, ResearchRole

router = APIRouter(prefix="/api/grants/opportunities", tags=["opportunities"])


class OpportunityCreate(BaseModel):
    title: str
    sponsor: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    geography: Optional[str] = None
    applicant_type: Optional[str] = None
    funding_type: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    currency: str = "KES"
    open_date: Optional[datetime] = None
    deadline: Optional[datetime] = None


class OpportunityOut(BaseModel):
    id: int
    title: str
    sponsor: Optional[str]
    description: Optional[str]
    category: Optional[str]
    amount_min: Optional[float]
    amount_max: Optional[float]
    currency: str
    deadline: Optional[datetime]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[OpportunityOut])
async def list_opportunities(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.GRANT_OFFICER, ResearchRole.PI,
        ResearchRole.INSTITUTIONAL_LEAD, ResearchRole.SYSTEM_ADMIN
    ]))
):
    query = select(GrantOpportunity).where(
        GrantOpportunity.institution_id == current_user.primary_institution_id
    )
    if status:
        query = query.where(GrantOpportunity.status == status)
    result = await db.execute(query.order_by(GrantOpportunity.deadline))
    return result.scalars().all()


@router.post("", response_model=OpportunityOut, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.GRANT_OFFICER, ResearchRole.SYSTEM_ADMIN
    ]))
):
    opp = GrantOpportunity(
        institution_id=current_user.primary_institution_id,
        created_by_id=current_user.id,
        **data.model_dump()
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return opp


@router.get("/{opp_id}", response_model=OpportunityOut)
async def get_opportunity(
    opp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.GRANT_OFFICER, ResearchRole.PI,
        ResearchRole.INSTITUTIONAL_LEAD, ResearchRole.SYSTEM_ADMIN
    ]))
):
    result = await db.execute(
        select(GrantOpportunity).where(
            GrantOpportunity.id == opp_id,
            GrantOpportunity.institution_id == current_user.primary_institution_id
        )
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    return opp


@router.patch("/{opp_id}/status")
async def update_opportunity_status(
    opp_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.GRANT_OFFICER]))
):
    result = await db.execute(select(GrantOpportunity).where(
        GrantOpportunity.id == opp_id,
        GrantOpportunity.institution_id == current_user.primary_institution_id
    ))
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    opp.status = status
    await db.commit()
    return {"id": opp_id, "status": status}
```

**`backend/routes/grants/proposals.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from database import get_db
from models import (Proposal, ProposalSection, ProposalDocument,
                    ProposalCollaborator, ProposalStatus, GrantOpportunity, User)
from auth import require_roles, ResearchRole
from services.workflow import can_transition_proposal
from services.notifications import create_notification
from services.file_upload import save_upload

router = APIRouter(prefix="/api/grants/proposals", tags=["proposals"])

DEFAULT_SECTIONS = [
    {"section_type": "executive_summary", "title": "Executive Summary"},
    {"section_type": "problem_statement", "title": "Problem Statement"},
    {"section_type": "methodology", "title": "Methodology"},
    {"section_type": "budget_justification", "title": "Budget Justification"},
    {"section_type": "mel_plan", "title": "M&E Plan"},
]


class ProposalCreate(BaseModel):
    opportunity_id: int
    title: str


class ProposalOut(BaseModel):
    id: int
    title: str
    status: str
    opportunity_id: int
    lead_pi_id: int
    current_version: int
    submitted_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SectionUpdate(BaseModel):
    content_html: str
    word_count: Optional[int] = 0


@router.post("", response_model=ProposalOut, status_code=201)
async def create_proposal(
    data: ProposalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.PI, ResearchRole.GRANT_OFFICER]))
):
    # Verify opportunity belongs to same institution
    opp = await db.get(GrantOpportunity, data.opportunity_id)
    if not opp or opp.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Opportunity not found")

    proposal = Proposal(
        opportunity_id=data.opportunity_id,
        institution_id=current_user.primary_institution_id,
        lead_pi_id=current_user.id,
        title=data.title,
    )
    db.add(proposal)
    await db.flush()  # get proposal.id before adding children

    # Create default sections
    for s in DEFAULT_SECTIONS:
        db.add(ProposalSection(proposal_id=proposal.id, **s))

    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.get("", response_model=List[ProposalOut])
async def list_proposals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PI, ResearchRole.GRANT_OFFICER,
        ResearchRole.RESEARCH_ADMIN, ResearchRole.INSTITUTIONAL_LEAD
    ]))
):
    query = select(Proposal).where(
        Proposal.institution_id == current_user.primary_institution_id
    )
    # PI sees only their own proposals
    if current_user.has_role(ResearchRole.PI) and not current_user.has_role(ResearchRole.GRANT_OFFICER):
        query = query.where(Proposal.lead_pi_id == current_user.id)

    result = await db.execute(query.order_by(Proposal.created_at.desc()))
    return result.scalars().all()


@router.get("/{proposal_id}")
async def get_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PI, ResearchRole.GRANT_OFFICER,
        ResearchRole.RESEARCH_ADMIN, ResearchRole.EXTERNAL_REVIEWER
    ]))
):
    result = await db.execute(
        select(Proposal)
        .options(
            selectinload(Proposal.sections),
            selectinload(Proposal.documents),
            selectinload(Proposal.collaborators),
            selectinload(Proposal.reviews),
        )
        .where(
            Proposal.id == proposal_id,
            Proposal.institution_id == current_user.primary_institution_id
        )
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    return proposal


@router.put("/{proposal_id}/sections/{section_id}")
async def update_section(
    proposal_id: int,
    section_id: int,
    data: SectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.PI, ResearchRole.GRANT_OFFICER]))
):
    result = await db.execute(
        select(ProposalSection).where(
            ProposalSection.id == section_id,
            ProposalSection.proposal_id == proposal_id,
        )
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(404, "Section not found")

    section.content_html = data.content_html
    section.word_count = data.word_count
    section.last_edited_by_id = current_user.id
    section.version += 1
    await db.commit()
    return {"id": section_id, "version": section.version}


@router.post("/{proposal_id}/documents", status_code=201)
async def upload_document(
    proposal_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.PI, ResearchRole.GRANT_OFFICER]))
):
    result = await db.execute(select(Proposal).where(
        Proposal.id == proposal_id,
        Proposal.institution_id == current_user.primary_institution_id
    ))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")

    file_info = await save_upload(file, subfolder="documents")
    doc = ProposalDocument(
        proposal_id=proposal_id,
        document_type=document_type,
        uploaded_by_id=current_user.id,
        **file_info,
    )
    db.add(doc)
    await db.commit()
    return {"id": doc.id, "filename": file_info["original_filename"]}


@router.patch("/{proposal_id}/status")
async def transition_proposal_status(
    proposal_id: int,
    target_status: ProposalStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PI, ResearchRole.GRANT_OFFICER, ResearchRole.RESEARCH_ADMIN
    ]))
):
    result = await db.execute(select(Proposal).where(
        Proposal.id == proposal_id,
        Proposal.institution_id == current_user.primary_institution_id
    ))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")

    if not can_transition_proposal(proposal.status, target_status):
        raise HTTPException(400, f"Cannot move from {proposal.status} to {target_status}")

    proposal.status = target_status
    if target_status == ProposalStatus.SUBMITTED:
        proposal.submitted_at = datetime.now(timezone.utc)

    await db.commit()

    # Notify PI if returned
    if target_status == ProposalStatus.RETURNED and proposal.lead_pi_id != current_user.id:
        await create_notification(
            db, proposal.lead_pi_id,
            title="Proposal returned for revision",
            message=f'Your proposal "{proposal.title}" requires revision.',
            entity_type="proposal", entity_id=proposal_id
        )

    return {"id": proposal_id, "status": target_status}
```

---

### Day 4 — Grant APIs: Reviews & Awards

**`backend/routes/grants/reviews.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone

from database import get_db
from models import ProposalReview, Proposal, ReviewStatus, ProposalStatus, User
from auth import require_roles, ResearchRole
from services.notifications import create_notification

router = APIRouter(prefix="/api/grants/reviews", tags=["reviews"])


class AssignReviewerRequest(BaseModel):
    reviewer_id: int


class SubmitReviewRequest(BaseModel):
    has_coi: bool
    coi_reason: Optional[str] = None
    scores: Optional[Dict[str, float]] = {}
    overall_score: Optional[float] = None
    recommendation: Optional[str] = None   # recommend / do_not_recommend / conditional
    narrative_feedback: Optional[str] = None


@router.post("/proposals/{proposal_id}/assign")
async def assign_reviewer(
    proposal_id: int,
    data: AssignReviewerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.GRANT_OFFICER]))
):
    proposal = await db.get(Proposal, proposal_id)
    if not proposal or proposal.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Proposal not found")

    # Check not already assigned
    existing = await db.execute(select(ProposalReview).where(
        ProposalReview.proposal_id == proposal_id,
        ProposalReview.reviewer_id == data.reviewer_id
    ))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Reviewer already assigned")

    review = ProposalReview(
        proposal_id=proposal_id,
        reviewer_id=data.reviewer_id,
    )
    db.add(review)

    # Advance proposal to under_review if not already
    if proposal.status == ProposalStatus.SUBMITTED:
        proposal.status = ProposalStatus.UNDER_REVIEW

    await db.commit()
    await create_notification(
        db, data.reviewer_id,
        title="Review assignment",
        message=f'You have been assigned to review: "{proposal.title}"',
        entity_type="proposal", entity_id=proposal_id
    )
    return {"message": "Reviewer assigned", "review_id": review.id}


@router.post("/{review_id}/submit")
async def submit_review(
    review_id: int,
    data: SubmitReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.EXTERNAL_REVIEWER, ResearchRole.GRANT_OFFICER
    ]))
):
    review = await db.get(ProposalReview, review_id)
    if not review or review.reviewer_id != current_user.id:
        raise HTTPException(403, "Not your review")

    review.has_coi = data.has_coi
    review.coi_reason = data.coi_reason
    review.scores = data.scores
    review.overall_score = data.overall_score
    review.recommendation = data.recommendation
    review.narrative_feedback = data.narrative_feedback
    review.status = ReviewStatus.SUBMITTED
    review.submitted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Review submitted"}


@router.get("/proposals/{proposal_id}")
async def get_proposal_reviews(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.GRANT_OFFICER]))
):
    result = await db.execute(
        select(ProposalReview).where(ProposalReview.proposal_id == proposal_id)
    )
    reviews = result.scalars().all()
    return reviews
```

**`backend/routes/grants/awards.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from database import get_db
from models import (Award, AwardStatus, BudgetLine, Proposal, ProposalStatus,
                    ResearchProject, ProjectStatus, User)
from auth import require_roles, ResearchRole
from services.notifications import create_notification

router = APIRouter(prefix="/api/grants/awards", tags=["awards"])


class AwardCreate(BaseModel):
    proposal_id: int
    funder_name: Optional[str] = None
    total_amount: float
    currency: str = "KES"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    conditions: Optional[str] = None


class BudgetLineCreate(BaseModel):
    category: str
    description: Optional[str] = None
    amount: float


class AwardOut(BaseModel):
    id: int
    award_number: str
    proposal_id: int
    total_amount: float
    currency: str
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    issued_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=AwardOut, status_code=201)
async def issue_award(
    data: AwardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.GRANT_OFFICER]))
):
    proposal = await db.get(Proposal, data.proposal_id)
    if not proposal or proposal.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Proposal not found")
    if proposal.status not in [ProposalStatus.UNDER_REVIEW, ProposalStatus.SUBMITTED]:
        raise HTTPException(400, f"Proposal in status {proposal.status} cannot be awarded")

    # Issue award
    award = Award(
        proposal_id=data.proposal_id,
        institution_id=current_user.primary_institution_id,
        award_number=f"AWD-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}",
        issued_by_id=current_user.id,
        **data.model_dump(exclude={"proposal_id"})
    )
    db.add(award)
    await db.flush()

    # Update proposal status
    proposal.status = ProposalStatus.AWARDED

    # ── Inter-module event: create linked Research Project ──────────────────
    project = ResearchProject(
        institution_id=current_user.primary_institution_id,
        award_id=award.id,
        pi_id=proposal.lead_pi_id,
        title=proposal.title,
        description=f"Auto-created from award {award.award_number}",
        project_type="funded",
        status=ProjectStatus.ACTIVE,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(project)
    # ────────────────────────────────────────────────────────────────────────

    await db.commit()
    await db.refresh(award)

    # Notify PI
    await create_notification(
        db, proposal.lead_pi_id,
        title="🎉 Award issued",
        message=f'Your proposal "{proposal.title}" has been awarded ({award.award_number}).',
        entity_type="award", entity_id=award.id
    )

    return award


@router.get("/{award_id}", response_model=AwardOut)
async def get_award(
    award_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.GRANT_OFFICER, ResearchRole.PI,
        ResearchRole.FINANCE_OFFICER, ResearchRole.INSTITUTIONAL_LEAD
    ]))
):
    award = await db.get(Award, award_id)
    if not award or award.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Award not found")
    return award


@router.post("/{award_id}/budget", status_code=201)
async def add_budget_lines(
    award_id: int,
    lines: List[BudgetLineCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.FINANCE_OFFICER, ResearchRole.GRANT_OFFICER
    ]))
):
    award = await db.get(Award, award_id)
    if not award or award.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Award not found")

    created = []
    for line_data in lines:
        line = BudgetLine(award_id=award_id, **line_data.model_dump())
        db.add(line)
        created.append(line)
    await db.commit()
    return {"created": len(created)}


@router.get("/{award_id}/budget")
async def get_budget(
    award_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.FINANCE_OFFICER, ResearchRole.GRANT_OFFICER,
        ResearchRole.PI, ResearchRole.INSTITUTIONAL_LEAD
    ]))
):
    result = await db.execute(
        select(BudgetLine).where(BudgetLine.award_id == award_id)
    )
    lines = result.scalars().all()
    total_budget = sum(l.amount for l in lines)
    total_spent = sum(l.spent_to_date for l in lines)
    return {
        "award_id": award_id,
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": total_budget - total_spent,
        "lines": lines,
    }
```

---

### Day 5 — Research & Data Capture APIs

**`backend/routes/research/projects.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import ResearchProject, ProjectStatus, User
from auth import require_roles, ResearchRole

router = APIRouter(prefix="/api/research/projects", tags=["research-projects"])


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_type: str = "independent"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    involves_human_subjects: bool = False


class ProjectOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    project_type: str
    status: str
    involves_human_subjects: bool
    award_id: Optional[int]
    pi_id: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PI, ResearchRole.RESEARCH_ADMIN,
        ResearchRole.INSTITUTIONAL_LEAD, ResearchRole.DATA_STEWARD
    ]))
):
    query = select(ResearchProject).where(
        ResearchProject.institution_id == current_user.primary_institution_id
    )
    if current_user.has_role(ResearchRole.PI) and not current_user.has_role(ResearchRole.RESEARCH_ADMIN):
        query = query.where(ResearchProject.pi_id == current_user.id)
    result = await db.execute(query.order_by(ResearchProject.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.PI, ResearchRole.RESEARCH_ADMIN]))
):
    project = ResearchProject(
        institution_id=current_user.primary_institution_id,
        pi_id=current_user.id,
        status=ProjectStatus.ACTIVE,
        **data.model_dump()
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PI, ResearchRole.RESEARCH_ADMIN,
        ResearchRole.ETHICS_REVIEWER, ResearchRole.DATA_STEWARD
    ]))
):
    project = await db.get(ResearchProject, project_id)
    if not project or project.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Project not found")
    return project
```

**`backend/routes/research/ethics.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from database import get_db
from models import EthicsApplication, EthicsStatus, ResearchProject, User
from auth import require_roles, ResearchRole
from services.workflow import can_transition_ethics
from services.notifications import create_notification

router = APIRouter(prefix="/api/research/ethics", tags=["ethics"])


class EthicsCreate(BaseModel):
    project_id: int
    application_type: str = "full_review"
    title: str
    lay_summary: Optional[str] = None
    methodology: Optional[str] = None
    risk_assessment: Optional[str] = None
    data_handling: Optional[str] = None


class EthicsOut(BaseModel):
    id: int
    project_id: int
    application_type: str
    status: str
    title: str
    submitted_at: Optional[datetime]
    approved_until: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=EthicsOut, status_code=201)
async def submit_ethics_application(
    data: EthicsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.PI, ResearchRole.RESEARCHER]))
):
    project = await db.get(ResearchProject, data.project_id)
    if not project or project.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Project not found")

    app = EthicsApplication(
        institution_id=current_user.primary_institution_id,
        submitted_by_id=current_user.id,
        status=EthicsStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
        **data.model_dump()
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/project/{project_id}", response_model=List[EthicsOut])
async def get_project_ethics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PI, ResearchRole.ETHICS_REVIEWER,
        ResearchRole.ETHICS_CHAIR, ResearchRole.RESEARCH_ADMIN
    ]))
):
    result = await db.execute(
        select(EthicsApplication).where(EthicsApplication.project_id == project_id)
    )
    return result.scalars().all()


@router.patch("/{app_id}/decision")
async def update_ethics_decision(
    app_id: int,
    target_status: EthicsStatus,
    decision_notes: Optional[str] = None,
    approved_until: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.ETHICS_CHAIR, ResearchRole.ETHICS_REVIEWER
    ]))
):
    app = await db.get(EthicsApplication, app_id)
    if not app or app.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Application not found")

    if not can_transition_ethics(app.status, target_status):
        raise HTTPException(400, f"Cannot move from {app.status} to {target_status}")

    app.status = target_status
    app.decision_notes = decision_notes
    if approved_until:
        app.approved_until = approved_until

    await db.commit()

    await create_notification(
        db, app.submitted_by_id,
        title=f"Ethics application: {target_status.value.replace('_', ' ').title()}",
        message=f'Your ethics application "{app.title}" has a new decision: {target_status.value}',
        entity_type="ethics", entity_id=app_id
    )
    return {"id": app_id, "status": target_status}
```

**`backend/routes/data/forms.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import csv
import io
import json

from database import get_db
from models import CaptureForm, FormSubmission, QAStatus, User
from auth import require_roles, ResearchRole

router = APIRouter(prefix="/api/data/forms", tags=["data-forms"])


class FormCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    source_system: str = "internal"
    external_form_id: Optional[str] = None
    external_endpoint: Optional[str] = None
    form_schema: Dict[str, Any] = {"fields": []}


class SubmissionCreate(BaseModel):
    data: Dict[str, Any]


class FormOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    source_system: str
    external_form_id: Optional[str]
    is_active: bool
    created_at: Any

    class Config:
        from_attributes = True


@router.post("", response_model=FormOut, status_code=201)
async def create_form(
    data: FormCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.DATA_STEWARD, ResearchRole.RESEARCHER, ResearchRole.PI
    ]))
):
    form = CaptureForm(
        institution_id=current_user.primary_institution_id,
        created_by_id=current_user.id,
        **data.model_dump()
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@router.get("", response_model=List[FormOut])
async def list_forms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.DATA_STEWARD, ResearchRole.RESEARCHER,
        ResearchRole.PI, ResearchRole.DATA_ENGINEER
    ]))
):
    result = await db.execute(
        select(CaptureForm).where(
            CaptureForm.institution_id == current_user.primary_institution_id
        )
    )
    return result.scalars().all()


@router.get("/{form_id}")
async def get_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.DATA_STEWARD, ResearchRole.RESEARCHER, ResearchRole.PI
    ]))
):
    form = await db.get(CaptureForm, form_id)
    if not form or form.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Form not found")
    return form


@router.post("/{form_id}/submissions", status_code=201)
async def submit_data(
    form_id: int,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.RESEARCHER, ResearchRole.PI, ResearchRole.DATA_STEWARD
    ]))
):
    form = await db.get(CaptureForm, form_id)
    if not form or form.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Form not found")

    submission = FormSubmission(
        form_id=form_id,
        data=data.data,
        submitted_by_id=current_user.id,
        source_system="internal",
    )
    db.add(submission)
    await db.commit()
    return {"id": submission.id, "status": "staged"}


@router.post("/{form_id}/upload-csv", status_code=201)
async def upload_csv(
    form_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([ResearchRole.DATA_STEWARD]))
):
    """Bulk upload submissions from a CSV file."""
    form = await db.get(CaptureForm, form_id)
    if not form or form.institution_id != current_user.primary_institution_id:
        raise HTTPException(404, "Form not found")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    created = 0
    for row in reader:
        submission = FormSubmission(
            form_id=form_id,
            data=dict(row),
            submitted_by_id=current_user.id,
            source_system="csv_upload",
        )
        db.add(submission)
        created += 1

    await db.commit()
    return {"created": created}


@router.get("/{form_id}/submissions")
async def list_submissions(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.DATA_STEWARD, ResearchRole.PI, ResearchRole.DATA_ENGINEER
    ]))
):
    result = await db.execute(
        select(FormSubmission).where(FormSubmission.form_id == form_id)
        .order_by(FormSubmission.submitted_at.desc())
    )
    submissions = result.scalars().all()
    return {
        "total": len(submissions),
        "staged": sum(1 for s in submissions if s.qa_status == QAStatus.STAGED),
        "passed": sum(1 for s in submissions if s.qa_status == QAStatus.PASSED),
        "failed": sum(1 for s in submissions if s.qa_status == QAStatus.FAILED),
        "submissions": submissions,
    }
```

### Day 5 (continued) — Wire up all routers in `main.py`

Add these imports and includes to `backend/main.py`:

```python
# Add to imports at top of main.py
from routes.grants.opportunities import router as opportunities_router
from routes.grants.proposals import router as proposals_router
from routes.grants.reviews import router as reviews_router
from routes.grants.awards import router as awards_router
from routes.research.projects import router as projects_router
from routes.research.ethics import router as ethics_router
from routes.data.forms import router as forms_router

# Add to router includes (after existing includes)
app.include_router(opportunities_router)
app.include_router(proposals_router)
app.include_router(reviews_router)
app.include_router(awards_router)
app.include_router(projects_router)
app.include_router(ethics_router)
app.include_router(forms_router)
```

Create empty `__init__.py` files:
```bash
touch backend/routes/grants/__init__.py
touch backend/routes/research/__init__.py
touch backend/routes/data/__init__.py
touch backend/schemas/__init__.py
```

Run migrations:
```bash
cd backend
alembic revision --autogenerate -m "prototype_all_modules"
alembic upgrade head
```

---

## 5. Week 2 — Frontend: Screens & Integration

---

### Day 6 — Shared Layout & API Client Extension

**`frontend/lib/apiModules.js`** — add all module API calls here:

```javascript
import api from './api';

// ─── GRANTS ──────────────────────────────────────────────────────────────────
export const opportunitiesApi = {
  list: (params) => api.get('/api/grants/opportunities', { params }),
  create: (data) => api.post('/api/grants/opportunities', data),
  get: (id) => api.get(`/api/grants/opportunities/${id}`),
  updateStatus: (id, status) =>
    api.patch(`/api/grants/opportunities/${id}/status`, null, { params: { status } }),
};

export const proposalsApi = {
  list: () => api.get('/api/grants/proposals'),
  create: (data) => api.post('/api/grants/proposals', data),
  get: (id) => api.get(`/api/grants/proposals/${id}`),
  updateSection: (proposalId, sectionId, data) =>
    api.put(`/api/grants/proposals/${proposalId}/sections/${sectionId}`, data),
  uploadDocument: (proposalId, file, documentType) => {
    const form = new FormData();
    form.append('file', file);
    form.append('document_type', documentType);
    return api.post(`/api/grants/proposals/${proposalId}/documents`, form);
  },
  transition: (id, status) =>
    api.patch(`/api/grants/proposals/${id}/status`, null, { params: { target_status: status } }),
};

export const reviewsApi = {
  assign: (proposalId, reviewerId) =>
    api.post(`/api/grants/reviews/proposals/${proposalId}/assign`, { reviewer_id: reviewerId }),
  submit: (reviewId, data) => api.post(`/api/grants/reviews/${reviewId}/submit`, data),
  getForProposal: (proposalId) => api.get(`/api/grants/reviews/proposals/${proposalId}`),
};

export const awardsApi = {
  issue: (data) => api.post('/api/grants/awards', data),
  get: (id) => api.get(`/api/grants/awards/${id}`),
  getBudget: (id) => api.get(`/api/grants/awards/${id}/budget`),
  addBudgetLines: (id, lines) => api.post(`/api/grants/awards/${id}/budget`, lines),
};

// ─── RESEARCH ────────────────────────────────────────────────────────────────
export const projectsApi = {
  list: () => api.get('/api/research/projects'),
  create: (data) => api.post('/api/research/projects', data),
  get: (id) => api.get(`/api/research/projects/${id}`),
};

export const ethicsApi = {
  submit: (data) => api.post('/api/research/ethics', data),
  getForProject: (projectId) => api.get(`/api/research/ethics/project/${projectId}`),
  decide: (id, status, notes) =>
    api.patch(`/api/research/ethics/${id}/decision`, null,
      { params: { target_status: status, decision_notes: notes } }),
};

// ─── DATA ────────────────────────────────────────────────────────────────────
export const formsApi = {
  list: () => api.get('/api/data/forms'),
  create: (data) => api.post('/api/data/forms', data),
  get: (id) => api.get(`/api/data/forms/${id}`),
  submit: (formId, data) => api.post(`/api/data/forms/${formId}/submissions`, { data }),
  uploadCsv: (formId, file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post(`/api/data/forms/${formId}/upload-csv`, form);
  },
  getSubmissions: (formId) => api.get(`/api/data/forms/${formId}/submissions`),
};

// ─── NOTIFICATIONS ───────────────────────────────────────────────────────────
export const notificationsApi = {
  list: () => api.get('/api/notifications'),
  markRead: (id) => api.patch(`/api/notifications/${id}/read`),
};
```

**`frontend/components/layout/AppShell.js`** — persistent layout with module navigation:

```javascript
'use client';
import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  Box, Drawer, AppBar, Toolbar, Typography, List, ListItem,
  ListItemIcon, ListItemText, ListItemButton, IconButton,
  Badge, Avatar, Divider, Chip
} from '@mui/material';
import {
  Assignment as GrantIcon,
  Science as ResearchIcon,
  Storage as DataIcon,
  Dashboard as DashboardIcon,
  Notifications as BellIcon,
  Menu as MenuIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
import { useAuthStore } from '../../store/authStore';

const DRAWER_WIDTH = 240;

const navItems = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { label: 'Grants', icon: <GrantIcon />, path: '/grants' },
  { label: 'Research', icon: <ResearchIcon />, path: '/research' },
  { label: 'Data', icon: <DataIcon />, path: '/data' },
];

export default function AppShell({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);

  const drawer = (
    <Box>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Box sx={{
          width: 36, height: 36, borderRadius: 1,
          background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <Typography sx={{ color: '#fff', fontWeight: 700, fontSize: 14 }}>D</Typography>
        </Box>
        <Typography variant="h6" fontWeight={700} sx={{ color: 'primary.main' }}>
          DACORIS
        </Typography>
      </Box>
      <Divider />
      <List>
        {navItems.map(({ label, icon, path }) => (
          <ListItem key={path} disablePadding>
            <ListItemButton
              selected={pathname.startsWith(path)}
              onClick={() => router.push(path)}
              sx={{ borderRadius: 1, mx: 1, my: 0.25 }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{icon}</ListItemIcon>
              <ListItemText primary={label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Chip
          label={user?.name || user?.email || 'User'}
          avatar={<Avatar sx={{ width: 24, height: 24 }}>{(user?.name || 'U')[0]}</Avatar>}
          variant="outlined"
          size="small"
          sx={{ width: '100%' }}
        />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton color="inherit" sx={{ mr: 1, display: { sm: 'none' } }}
            onClick={() => setMobileOpen(!mobileOpen)}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }} />
          <IconButton color="inherit">
            <Badge badgeContent={3} color="error">
              <BellIcon />
            </Badge>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Desktop drawer */}
      <Drawer variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          width: DRAWER_WIDTH,
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' },
        }}>
        {drawer}
      </Drawer>

      {/* Mobile drawer */}
      <Drawer variant="temporary" open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        sx={{ display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}>
        {drawer}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8, ml: { sm: `${DRAWER_WIDTH}px` } }}>
        {children}
      </Box>
    </Box>
  );
}
```

---

### Day 7 — Grant: Opportunities & Proposal Workspace

**`frontend/app/grants/page.js`** — Opportunities list:

```javascript
'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Typography, Button, Card, CardContent, CardActions,
  Grid, Chip, Skeleton, Alert
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import AppShell from '../../components/layout/AppShell';
import { opportunitiesApi } from '../../lib/apiModules';
import dayjs from 'dayjs';

export default function GrantsPage() {
  const router = useRouter();
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    opportunitiesApi.list()
      .then(r => setOpportunities(r.data))
      .catch(() => setError('Failed to load opportunities'))
      .finally(() => setLoading(false));
  }, []);

  const statusColor = { open: 'success', closed: 'default', upcoming: 'info' };

  return (
    <AppShell>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" fontWeight={700}>Funding Opportunities</Typography>
        <Button variant="contained" startIcon={<AddIcon />}
          onClick={() => router.push('/grants/new')}>
          New Opportunity
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={2}>
        {loading ? Array(4).fill(0).map((_, i) => (
          <Grid item xs={12} md={6} key={i}>
            <Skeleton variant="rectangular" height={160} sx={{ borderRadius: 2 }} />
          </Grid>
        )) : opportunities.map(opp => (
          <Grid item xs={12} md={6} key={opp.id}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Chip label={opp.status} size="small"
                    color={statusColor[opp.status] || 'default'} />
                  {opp.deadline && (
                    <Typography variant="caption" color="text.secondary">
                      Due: {dayjs(opp.deadline).format('DD MMM YYYY')}
                    </Typography>
                  )}
                </Box>
                <Typography variant="h6" fontSize={16} fontWeight={600} gutterBottom>
                  {opp.title}
                </Typography>
                {opp.sponsor && (
                  <Typography variant="body2" color="text.secondary">
                    {opp.sponsor}
                  </Typography>
                )}
                {opp.amount_max && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Up to {opp.currency} {opp.amount_max?.toLocaleString()}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => router.push(`/grants/${opp.id}`)}>
                  View
                </Button>
                <Button size="small" variant="outlined"
                  onClick={() => router.push(`/grants/proposals/new?opp=${opp.id}`)}>
                  Apply
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </AppShell>
  );
}
```

**`frontend/app/grants/proposals/[id]/page.js`** — Proposal workspace with section editor:

```javascript
'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box, Typography, Paper, Tabs, Tab, Button, Chip,
  LinearProgress, Alert, TextField, Stack, Divider,
  List, ListItem, ListItemText, ListItemIcon, IconButton
} from '@mui/material';
import {
  CloudUpload as UploadIcon, Send as SubmitIcon,
  Description as DocIcon, Delete as DeleteIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import AppShell from '../../../../components/layout/AppShell';
import { proposalsApi } from '../../../../lib/apiModules';

const STATUS_COLORS = {
  draft: 'default', internal_review: 'warning',
  submitted: 'info', under_review: 'primary',
  awarded: 'success', declined: 'error',
};

export default function ProposalWorkspace() {
  const { id } = useParams();
  const router = useRouter();
  const [proposal, setProposal] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [saving, setSaving] = useState(false);
  const [sectionContent, setSectionContent] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    proposalsApi.get(id).then(r => {
      setProposal(r.data);
      // Initialize section content from loaded data
      const content = {};
      r.data.sections?.forEach(s => { content[s.id] = s.content_html || ''; });
      setSectionContent(content);
    }).catch(() => setError('Failed to load proposal'));
  }, [id]);

  const saveSection = async (section) => {
    setSaving(true);
    try {
      await proposalsApi.updateSection(id, section.id, {
        content_html: sectionContent[section.id] || '',
        word_count: (sectionContent[section.id] || '').split(/\s+/).filter(Boolean).length,
      });
      setSuccess('Section saved');
      setTimeout(() => setSuccess(''), 2000);
    } catch {
      setError('Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (e, docType) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await proposalsApi.uploadDocument(id, file, docType);
      const updated = await proposalsApi.get(id);
      setProposal(updated.data);
    } catch {
      setError('Upload failed');
    }
  };

  const submitForReview = async () => {
    try {
      await proposalsApi.transition(id, 'internal_review');
      const updated = await proposalsApi.get(id);
      setProposal(updated.data);
      setSuccess('Submitted for internal review');
    } catch (err) {
      setError(err.response?.data?.detail || 'Submission failed');
    }
  };

  // Completion meter
  const completedSections = proposal?.sections?.filter(
    s => (sectionContent[s.id] || s.content_html || '').trim().length > 50
  ).length || 0;
  const totalSections = proposal?.sections?.length || 1;
  const completionPct = Math.round((completedSections / totalSections) * 100);

  if (!proposal) return <AppShell><LinearProgress /></AppShell>;

  const sections = proposal.sections || [];
  const documents = proposal.documents || [];

  return (
    <AppShell>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <Typography variant="h5" fontWeight={700} sx={{ flexGrow: 1 }}>
            {proposal.title}
          </Typography>
          <Chip label={proposal.status.replace('_', ' ')}
            color={STATUS_COLORS[proposal.status] || 'default'} />
        </Box>

        {/* Completion meter */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LinearProgress variant="determinate" value={completionPct}
            sx={{ flexGrow: 1, height: 8, borderRadius: 4 }} />
          <Typography variant="body2" color="text.secondary">
            {completionPct}% complete ({completedSections}/{totalSections} sections)
          </Typography>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
        <Tab label="Sections" />
        <Tab label={`Documents (${documents.length})`} />
      </Tabs>

      {/* SECTIONS TAB */}
      {activeTab === 0 && (
        <Stack spacing={2}>
          {sections.map((section, i) => (
            <Paper key={section.id} variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography fontWeight={600}>{section.title}</Typography>
                <Button size="small" startIcon={<SaveIcon />}
                  onClick={() => saveSection(section)} disabled={saving}>
                  Save
                </Button>
              </Box>
              <TextField
                multiline minRows={6} fullWidth
                placeholder={`Write the ${section.title}...`}
                value={sectionContent[section.id] || ''}
                onChange={e => setSectionContent(prev => ({
                  ...prev, [section.id]: e.target.value
                }))}
                variant="outlined"
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {(sectionContent[section.id] || '').split(/\s+/).filter(Boolean).length} words
              </Typography>
            </Paper>
          ))}
        </Stack>
      )}

      {/* DOCUMENTS TAB */}
      {activeTab === 1 && (
        <Box>
          <Button variant="outlined" component="label" startIcon={<UploadIcon />} sx={{ mb: 2 }}>
            Upload Document
            <input type="file" hidden accept=".pdf,.doc,.docx,.xlsx,.csv"
              onChange={e => handleUpload(e, 'supporting_document')} />
          </Button>
          <List>
            {documents.map(doc => (
              <ListItem key={doc.id} divider>
                <ListItemIcon><DocIcon /></ListItemIcon>
                <ListItemText
                  primary={doc.original_filename}
                  secondary={`${doc.document_type} • ${(doc.file_size_bytes / 1024).toFixed(1)} KB`}
                />
              </ListItem>
            ))}
            {documents.length === 0 && (
              <Typography color="text.secondary" sx={{ p: 2 }}>
                No documents uploaded yet.
              </Typography>
            )}
          </List>
        </Box>
      )}

      {/* Submit button */}
      {proposal.status === 'draft' && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" size="large" startIcon={<SubmitIcon />}
            onClick={submitForReview} disabled={completionPct < 50}>
            Submit for Internal Review
          </Button>
        </Box>
      )}
    </AppShell>
  );
}
```

---

### Day 8 — Review Console & Award Screen

**`frontend/app/review/[id]/page.js`** — Reviewer scoring UI:

```javascript
'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Box, Typography, Paper, Slider, TextField, Button,
  FormControl, InputLabel, Select, MenuItem, Alert,
  Divider, Chip, LinearProgress
} from '@mui/material';
import AppShell from '../../../components/layout/AppShell';
import { reviewsApi, proposalsApi } from '../../../lib/apiModules';

const CRITERIA = [
  { key: 'relevance', label: 'Relevance & Innovation', max: 25 },
  { key: 'methodology', label: 'Methodology', max: 25 },
  { key: 'feasibility', label: 'Feasibility & Team', max: 25 },
  { key: 'impact', label: 'Expected Impact', max: 25 },
];

export default function ReviewPage() {
  const { id } = useParams();   // review_id
  const [scores, setScores] = useState({ relevance: 0, methodology: 0, feasibility: 0, impact: 0 });
  const [recommendation, setRecommendation] = useState('');
  const [narrative, setNarrative] = useState('');
  const [hasCoi, setHasCoi] = useState(false);
  const [coiReason, setCoiReason] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const totalScore = Object.values(scores).reduce((a, b) => a + b, 0);

  const submit = async () => {
    try {
      await reviewsApi.submit(id, {
        has_coi: hasCoi,
        coi_reason: hasCoi ? coiReason : null,
        scores,
        overall_score: totalScore,
        recommendation,
        narrative_feedback: narrative,
      });
      setSubmitted(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Submission failed');
    }
  };

  if (submitted) return (
    <AppShell>
      <Alert severity="success" sx={{ mt: 4 }}>
        Review submitted successfully. Thank you for your assessment.
      </Alert>
    </AppShell>
  );

  return (
    <AppShell>
      <Typography variant="h5" fontWeight={700} gutterBottom>Review Console</Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* COI declaration */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography fontWeight={600} gutterBottom>Conflict of Interest Declaration</Typography>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Do you have a COI?</InputLabel>
          <Select value={hasCoi} label="Do you have a COI?"
            onChange={e => setHasCoi(e.target.value)}>
            <MenuItem value={false}>No conflict of interest</MenuItem>
            <MenuItem value={true}>I declare a conflict</MenuItem>
          </Select>
        </FormControl>
        {hasCoi && (
          <TextField fullWidth multiline rows={2} label="Describe the conflict"
            value={coiReason} onChange={e => setCoiReason(e.target.value)}
            sx={{ mt: 2 }} />
        )}
      </Paper>

      {/* Scoring rubric */}
      {!hasCoi && (
        <>
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography fontWeight={600}>Scoring Rubric</Typography>
              <Chip label={`Total: ${totalScore}/100`}
                color={totalScore >= 70 ? 'success' : totalScore >= 50 ? 'warning' : 'error'}
                variant="outlined" />
            </Box>
            {CRITERIA.map(c => (
              <Box key={c.key} sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight={500}>{c.label}</Typography>
                  <Typography variant="body2" color="primary">{scores[c.key]} / {c.max}</Typography>
                </Box>
                <Slider
                  value={scores[c.key]}
                  onChange={(_, v) => setScores(prev => ({ ...prev, [c.key]: v }))}
                  min={0} max={c.max} step={1} marks valueLabelDisplay="auto"
                  sx={{ mt: 1 }}
                />
              </Box>
            ))}
          </Paper>

          {/* Recommendation & narrative */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Typography fontWeight={600} gutterBottom>Recommendation</Typography>
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Recommendation</InputLabel>
              <Select value={recommendation} label="Recommendation"
                onChange={e => setRecommendation(e.target.value)}>
                <MenuItem value="recommend">Recommend for funding</MenuItem>
                <MenuItem value="conditional">Conditional recommendation</MenuItem>
                <MenuItem value="do_not_recommend">Do not recommend</MenuItem>
              </Select>
            </FormControl>
            <TextField fullWidth multiline rows={5}
              label="Narrative feedback (sent to applicant)"
              value={narrative} onChange={e => setNarrative(e.target.value)} />
          </Paper>

          <Button variant="contained" size="large" onClick={submit}
            disabled={!recommendation || !narrative}>
            Submit Review
          </Button>
        </>
      )}
    </AppShell>
  );
}
```

---

### Day 9 — Research: Project & Ethics Screens

**`frontend/app/research/page.js`** — Projects list and register button:

```javascript
'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Typography, Button, Card, CardContent, CardActions,
  Grid, Chip, Skeleton, Alert
} from '@mui/material';
import { Add as AddIcon, Science as ScienceIcon } from '@mui/icons-material';
import AppShell from '../../components/layout/AppShell';
import { projectsApi } from '../../lib/apiModules';
import dayjs from 'dayjs';

const STATUS_COLOR = {
  active: 'success', proposed: 'warning',
  suspended: 'error', completed: 'default'
};

export default function ResearchPage() {
  const router = useRouter();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.list().then(r => setProjects(r.data)).finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" fontWeight={700}>Research Projects</Typography>
        <Button variant="contained" startIcon={<AddIcon />}
          onClick={() => router.push('/research/new')}>
          Register Project
        </Button>
      </Box>

      <Grid container spacing={2}>
        {loading ? Array(3).fill(0).map((_, i) => (
          <Grid item xs={12} md={6} key={i}>
            <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
          </Grid>
        )) : projects.map(p => (
          <Grid item xs={12} md={6} key={p.id}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <Chip size="small" label={p.status} color={STATUS_COLOR[p.status]} />
                  <Chip size="small" label={p.project_type} variant="outlined" />
                  {p.involves_human_subjects && (
                    <Chip size="small" label="Human subjects" color="warning" variant="outlined" />
                  )}
                </Box>
                <Typography fontWeight={600} gutterBottom>{p.title}</Typography>
                {p.start_date && (
                  <Typography variant="caption" color="text.secondary">
                    {dayjs(p.start_date).format('MMM YYYY')} –{' '}
                    {p.end_date ? dayjs(p.end_date).format('MMM YYYY') : 'Ongoing'}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => router.push(`/research/${p.id}`)}>
                  Open
                </Button>
                {p.involves_human_subjects && (
                  <Button size="small" onClick={() =>
                    router.push(`/research/ethics/new?project=${p.id}`)}>
                    Ethics Application
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </AppShell>
  );
}
```

---

### Day 10 — Data Capture: Form Builder & Submission View

**`frontend/app/data/forms/new/page.js`** — Basic form builder with field types:

```javascript
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Typography, TextField, Button, Paper, Stack,
  Select, MenuItem, FormControl, InputLabel, IconButton,
  Divider, Alert, Chip, Switch, FormControlLabel
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Save as SaveIcon } from '@mui/icons-material';
import AppShell from '../../../../components/layout/AppShell';
import { formsApi } from '../../../../lib/apiModules';

const FIELD_TYPES = [
  { value: 'text', label: 'Short Text' },
  { value: 'textarea', label: 'Long Text' },
  { value: 'integer', label: 'Number (integer)' },
  { value: 'decimal', label: 'Number (decimal)' },
  { value: 'date', label: 'Date' },
  { value: 'select_one', label: 'Single Choice' },
  { value: 'select_multiple', label: 'Multiple Choice' },
  { value: 'geopoint', label: 'GPS Location' },
  { value: 'image', label: 'Photo' },
];

const newField = () => ({
  id: Date.now(),
  name: '',
  label: '',
  type: 'text',
  required: false,
  hint: '',
  choices: '',      // comma-separated for select types
});

export default function FormBuilderPage() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [sourceSystem, setSourceSystem] = useState('internal');
  const [externalFormId, setExternalFormId] = useState('');
  const [externalEndpoint, setExternalEndpoint] = useState('');
  const [fields, setFields] = useState([newField()]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const addField = () => setFields(prev => [...prev, newField()]);
  const removeField = (id) => setFields(prev => prev.filter(f => f.id !== id));
  const updateField = (id, key, value) =>
    setFields(prev => prev.map(f => f.id === id ? { ...f, [key]: value } : f));

  const save = async () => {
    if (!title.trim()) { setError('Form title is required'); return; }
    setSaving(true);
    try {
      const schema = {
        fields: fields.map(f => ({
          name: f.name || `field_${f.id}`,
          label: f.label || f.name,
          type: f.type,
          required: f.required,
          hint: f.hint,
          choices: f.choices ? f.choices.split(',').map(c => c.trim()) : undefined,
        }))
      };
      const res = await formsApi.create({
        title, description, source_system: sourceSystem,
        external_form_id: externalFormId || null,
        external_endpoint: externalEndpoint || null,
        form_schema: schema,
      });
      router.push(`/data/forms/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create form');
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell>
      <Typography variant="h5" fontWeight={700} gutterBottom>New Capture Form</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      {/* Form metadata */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography fontWeight={600} gutterBottom>Form Details</Typography>
        <Stack spacing={2}>
          <TextField label="Form Title" value={title}
            onChange={e => setTitle(e.target.value)} required fullWidth />
          <TextField label="Description" value={description}
            onChange={e => setDescription(e.target.value)} multiline rows={2} fullWidth />

          <FormControl fullWidth size="small">
            <InputLabel>Data Collection Tool</InputLabel>
            <Select value={sourceSystem} label="Data Collection Tool"
              onChange={e => setSourceSystem(e.target.value)}>
              <MenuItem value="internal">DACORIS Native Form</MenuItem>
              <MenuItem value="kobo">KoBoToolbox (link existing)</MenuItem>
              <MenuItem value="odk">ODK Central (link existing)</MenuItem>
              <MenuItem value="redcap">REDCap (link existing)</MenuItem>
              <MenuItem value="csv">CSV Upload only</MenuItem>
            </Select>
          </FormControl>

          {sourceSystem !== 'internal' && sourceSystem !== 'csv' && (
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Link to external form — DACORIS will pull submissions automatically.
              </Typography>
              <Stack spacing={1}>
                <TextField size="small" fullWidth
                  label={`${sourceSystem === 'kobo' ? 'KoBoToolbox Form UID' :
                          sourceSystem === 'odk' ? 'ODK Form ID' : 'REDCap Project ID'}`}
                  value={externalFormId}
                  onChange={e => setExternalFormId(e.target.value)} />
                <TextField size="small" fullWidth
                  label="API Endpoint URL"
                  placeholder={sourceSystem === 'kobo'
                    ? 'https://kf.kobotoolbox.org/api/v2/assets/{uid}/submissions/'
                    : 'https://your-odk-server/v1/projects/{id}/submissions'}
                  value={externalEndpoint}
                  onChange={e => setExternalEndpoint(e.target.value)} />
              </Stack>
            </Box>
          )}
        </Stack>
      </Paper>

      {/* Field builder */}
      {(sourceSystem === 'internal') && (
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography fontWeight={600}>Form Fields</Typography>
            <Button size="small" startIcon={<AddIcon />} onClick={addField}>Add Field</Button>
          </Box>

          <Stack spacing={2}>
            {fields.map((field, idx) => (
              <Box key={field.id} sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Chip size="small" label={`Field ${idx + 1}`} variant="outlined" />
                  <IconButton size="small" onClick={() => removeField(field.id)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                  <TextField size="small" label="Field Name (no spaces)"
                    value={field.name} fullWidth
                    onChange={e => updateField(field.id, 'name',
                      e.target.value.replace(/\s+/g, '_').toLowerCase())} />
                  <TextField size="small" label="Label (shown to user)"
                    value={field.label} fullWidth
                    onChange={e => updateField(field.id, 'label', e.target.value)} />
                  <FormControl size="small" sx={{ minWidth: 160 }}>
                    <InputLabel>Type</InputLabel>
                    <Select value={field.type} label="Type"
                      onChange={e => updateField(field.id, 'type', e.target.value)}>
                      {FIELD_TYPES.map(t => (
                        <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Stack>
                {['select_one', 'select_multiple'].includes(field.type) && (
                  <TextField size="small" fullWidth sx={{ mt: 1 }}
                    label="Choices (comma-separated)"
                    placeholder="Option A, Option B, Option C"
                    value={field.choices}
                    onChange={e => updateField(field.id, 'choices', e.target.value)} />
                )}
                <FormControlLabel control={
                  <Switch checked={field.required}
                    onChange={e => updateField(field.id, 'required', e.target.checked)} />
                } label="Required" sx={{ mt: 1 }} />
              </Box>
            ))}
          </Stack>
        </Paper>
      )}

      <Button variant="contained" size="large" startIcon={<SaveIcon />}
        onClick={save} disabled={saving}>
        {saving ? 'Saving...' : 'Save Form'}
      </Button>
    </AppShell>
  );
}
```

---

### Day 11 — Notifications API & Dashboard Update

**Add to `backend/routes/__init__.py`** or create a new `backend/routes/notifications.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Notification, User
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("")
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
    )
    notifications = result.scalars().all()
    return {
        "unread": sum(1 for n in notifications if not n.is_read),
        "items": notifications,
    }

@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    n = await db.get(Notification, notification_id)
    if n and n.user_id == current_user.id:
        n.is_read = True
        await db.commit()
    return {"ok": True}
```

---

### Day 12 — Seed Data & Demo Prep

---

## 6. Database Migrations Reference

```bash
# Create a new migration after model changes
cd backend
alembic revision --autogenerate -m "describe_the_change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Check current migration state
alembic current

# View migration history
alembic history --verbose

# If you need a clean slate during development (DESTROYS ALL DATA)
python drop_and_recreate.py
alembic stamp head   # tells alembic the DB is at current state
```

---

## 7. Seed Data Script

Save as `backend/seed.py` and run with `python seed.py`:

```python
"""
Prototype seed script — creates demo institution, users, and sample data.
Run once after database initialisation.
Usage: python seed.py
"""
import asyncio
from datetime import datetime, timezone, timedelta
from database import AsyncSessionLocal
from models import (
    Institution, User, AccountType, UserStatus,
    GrantOpportunity, Proposal, ProposalSection, ProposalStatus,
    Award, AwardStatus, BudgetLine,
    ResearchProject, ProjectStatus,
    EthicsApplication, EthicsStatus,
    CaptureForm,
)
from auth import get_password_hash

DEMO_INSTITUTION = {
    "name": "Demo Research University",
    "domain": "demo.ac.ke",
    "verified_domains": "demo.ac.ke",
    "is_active": True,
}

async def seed():
    async with AsyncSessionLocal() as db:
        # ── Institution ─────────────────────────────────────────────────────
        inst = Institution(**DEMO_INSTITUTION)
        db.add(inst)
        await db.flush()

        # ── Users ───────────────────────────────────────────────────────────
        users = {}
        user_data = [
            {"email": "pi@demo.ac.ke",        "name": "Dr. Amina Odhiambo",  "role": "pi"},
            {"email": "grant@demo.ac.ke",      "name": "James Kariuki",        "role": "grant_officer"},
            {"email": "finance@demo.ac.ke",    "name": "Grace Waweru",         "role": "finance_officer"},
            {"email": "reviewer@demo.ac.ke",   "name": "Prof. David Mutua",    "role": "external_reviewer"},
            {"email": "ethics@demo.ac.ke",     "name": "Dr. Fatuma Hassan",    "role": "ethics_chair"},
            {"email": "data@demo.ac.ke",       "name": "Brian Otieno",         "role": "data_steward"},
        ]
        for u in user_data:
            user = User(
                email=u["email"],
                name=u["name"],
                hashed_password=get_password_hash("Demo@12345"),
                account_type=AccountType.ORCID,   # use local password for demo
                status=UserStatus.ACTIVE,
                primary_institution_id=inst.id,
            )
            db.add(user)
            await db.flush()
            users[u["role"]] = user

        # ── Grant Opportunity ─────────────────────────────────────────────
        opp = GrantOpportunity(
            institution_id=inst.id,
            title="Digital Health Innovation Grant 2026",
            sponsor="Kenya National Research Fund",
            description="Funding digital health solutions for rural communities.",
            category="Health Technology",
            geography="Kenya",
            applicant_type="Research Institution",
            funding_type="competitive_grant",
            amount_min=500_000,
            amount_max=2_000_000,
            currency="KES",
            open_date=datetime.now(timezone.utc),
            deadline=datetime.now(timezone.utc) + timedelta(days=45),
            status="open",
            created_by_id=users["grant_officer"].id,
        )
        db.add(opp)
        await db.flush()

        # ── Proposal ─────────────────────────────────────────────────────
        proposal = Proposal(
            opportunity_id=opp.id,
            institution_id=inst.id,
            lead_pi_id=users["pi"].id,
            title="Mobile-Based Maternal Health Monitoring System",
            status=ProposalStatus.DRAFT,
        )
        db.add(proposal)
        await db.flush()

        sections = [
            ("executive_summary", "Executive Summary",
             "<p>This project develops a mobile-based system to monitor maternal health indicators in rural Kenya, targeting a 30% reduction in preventable maternal deaths.</p>"),
            ("problem_statement", "Problem Statement",
             "<p>Rural communities lack access to consistent prenatal care. This system bridges the gap using SMS and offline-capable mobile apps.</p>"),
            ("methodology", "Methodology",
             "<p>Mixed-methods approach: quantitative health tracking via ODK forms and qualitative FGDs with community health workers.</p>"),
            ("budget_justification", "Budget Justification", ""),
            ("mel_plan", "M&E Plan", ""),
        ]
        for stype, stitle, content in sections:
            db.add(ProposalSection(
                proposal_id=proposal.id,
                section_type=stype,
                title=stitle,
                content_html=content,
                word_count=len(content.split()),
            ))

        # ── Award (for a separate funded project) ─────────────────────────
        opp2 = GrantOpportunity(
            institution_id=inst.id,
            title="Climate Resilience Research Fund",
            sponsor="African Development Bank",
            description="Research on climate adaptation for smallholder farmers.",
            amount_max=5_000_000,
            currency="KES",
            deadline=datetime.now(timezone.utc) - timedelta(days=30),
            status="closed",
            created_by_id=users["grant_officer"].id,
        )
        db.add(opp2)
        await db.flush()

        funded_proposal = Proposal(
            opportunity_id=opp2.id,
            institution_id=inst.id,
            lead_pi_id=users["pi"].id,
            title="Drought-Resistant Crop Varieties for Arid Regions",
            status=ProposalStatus.AWARDED,
            submitted_at=datetime.now(timezone.utc) - timedelta(days=20),
        )
        db.add(funded_proposal)
        await db.flush()

        award = Award(
            proposal_id=funded_proposal.id,
            institution_id=inst.id,
            award_number="AWD-2026-DEMO01",
            funder_name="African Development Bank",
            total_amount=3_500_000,
            currency="KES",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=730),
            status=AwardStatus.ACTIVE,
            issued_by_id=users["grant_officer"].id,
        )
        db.add(award)
        await db.flush()

        budget_lines = [
            ("Personnel", "PI and RA salaries", 1_400_000),
            ("Equipment", "Lab equipment and sensors", 700_000),
            ("Field Work", "Travel and data collection", 500_000),
            ("Overhead", "Institutional overhead 20%", 700_000),
            ("Publications", "Open access fees", 200_000),
        ]
        for cat, desc, amt in budget_lines:
            db.add(BudgetLine(award_id=award.id, category=cat, description=desc, amount=amt))

        # ── Research Project ──────────────────────────────────────────────
        project = ResearchProject(
            institution_id=inst.id,
            award_id=award.id,
            pi_id=users["pi"].id,
            title="Drought-Resistant Crop Varieties for Arid Regions",
            description="Field research on improved crop varieties in Baringo County.",
            project_type="funded",
            status=ProjectStatus.ACTIVE,
            involves_human_subjects=True,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=730),
        )
        db.add(project)
        await db.flush()

        # ── Ethics Application ────────────────────────────────────────────
        db.add(EthicsApplication(
            project_id=project.id,
            institution_id=inst.id,
            application_type="full_review",
            status=EthicsStatus.SUBMITTED,
            title="Human Subjects Ethics Application: Drought Research",
            lay_summary="Research involving smallholder farmers via structured interviews.",
            methodology="Household surveys and FGDs with 200 farmers across 3 counties.",
            risk_assessment="Minimal risk. Informed consent will be obtained.",
            data_handling="Data pseudonymised, stored on institutional servers only.",
            submitted_by_id=users["pi"].id,
            submitted_at=datetime.now(timezone.utc) - timedelta(days=5),
        ))

        # ── Capture Form ──────────────────────────────────────────────────
        db.add(CaptureForm(
            institution_id=inst.id,
            project_id=project.id,
            title="Farmer Baseline Survey",
            description="Baseline socioeconomic and agricultural data collection from farmers.",
            source_system="kobo",
            external_form_id="aXdemo123",
            external_endpoint="https://kf.kobotoolbox.org/api/v2/assets/aXdemo123/data/",
            form_schema={
                "fields": [
                    {"name": "farmer_name", "label": "Farmer Name", "type": "text", "required": True},
                    {"name": "county", "label": "County", "type": "select_one",
                     "choices": ["Baringo", "Laikipia", "Turkana"], "required": True},
                    {"name": "farm_size_acres", "label": "Farm Size (acres)", "type": "decimal"},
                    {"name": "primary_crop", "label": "Primary Crop", "type": "text"},
                    {"name": "has_irrigation", "label": "Has Irrigation?",
                     "type": "select_one", "choices": ["Yes", "No"]},
                    {"name": "gps_location", "label": "Farm GPS Location", "type": "geopoint"},
                ]
            },
            created_by_id=users["data_steward"].id,
        ))

        await db.commit()
        print("✅ Seed data created successfully!")
        print("\n📋 Demo Login Credentials (password: Demo@12345 for all):")
        for u in user_data:
            print(f"  {u['role']:20s} → {u['email']}")
        print(f"\n🏛️  Institution: {DEMO_INSTITUTION['name']}")
        print(f"📊  Opportunity: Digital Health Innovation Grant 2026")
        print(f"📄  Proposal in DRAFT: Mobile-Based Maternal Health Monitoring System")
        print(f"🏆  Funded award: AWD-2026-DEMO01 (KES 3,500,000)")
        print(f"🔬  Active project with ethics application submitted")
        print(f"📋  Capture form: Farmer Baseline Survey (KoBoToolbox linked)")

if __name__ == "__main__":
    asyncio.run(seed())
```

Run it:
```bash
cd backend
python seed.py
```

---

## 8. API Reference (Prototype Endpoints)

Full list of endpoints available after prototype is running. Test all at `http://localhost:8000/docs`.

### Auth (existing)
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/login` | Admin email/password login |
| GET | `/api/auth/orcid/login` | ORCID OAuth redirect |
| GET | `/api/auth/orcid/callback` | ORCID OAuth callback |
| GET | `/api/auth/me` | Current user info |

### Grant Opportunities
| Method | Path | Roles |
|---|---|---|
| GET | `/api/grants/opportunities` | GRANT_OFFICER, PI, INSTITUTIONAL_LEAD |
| POST | `/api/grants/opportunities` | GRANT_OFFICER |
| GET | `/api/grants/opportunities/{id}` | GRANT_OFFICER, PI |
| PATCH | `/api/grants/opportunities/{id}/status` | GRANT_OFFICER |

### Grant Proposals
| Method | Path | Roles |
|---|---|---|
| POST | `/api/grants/proposals` | PI, GRANT_OFFICER |
| GET | `/api/grants/proposals` | PI (own), GRANT_OFFICER (all) |
| GET | `/api/grants/proposals/{id}` | PI, GRANT_OFFICER, EXTERNAL_REVIEWER |
| PUT | `/api/grants/proposals/{id}/sections/{sid}` | PI, GRANT_OFFICER |
| POST | `/api/grants/proposals/{id}/documents` | PI, GRANT_OFFICER |
| PATCH | `/api/grants/proposals/{id}/status` | PI, GRANT_OFFICER, RESEARCH_ADMIN |

### Reviews & Awards
| Method | Path | Roles |
|---|---|---|
| POST | `/api/grants/reviews/proposals/{id}/assign` | GRANT_OFFICER |
| POST | `/api/grants/reviews/{id}/submit` | EXTERNAL_REVIEWER, GRANT_OFFICER |
| GET | `/api/grants/reviews/proposals/{id}` | GRANT_OFFICER |
| POST | `/api/grants/awards` | GRANT_OFFICER |
| GET | `/api/grants/awards/{id}` | GRANT_OFFICER, PI, FINANCE_OFFICER |
| POST | `/api/grants/awards/{id}/budget` | FINANCE_OFFICER, GRANT_OFFICER |
| GET | `/api/grants/awards/{id}/budget` | FINANCE_OFFICER, GRANT_OFFICER, PI |

### Research Projects & Ethics
| Method | Path | Roles |
|---|---|---|
| GET | `/api/research/projects` | PI, RESEARCH_ADMIN |
| POST | `/api/research/projects` | PI, RESEARCH_ADMIN |
| GET | `/api/research/projects/{id}` | PI, RESEARCH_ADMIN, ETHICS_REVIEWER |
| POST | `/api/research/ethics` | PI, RESEARCHER |
| GET | `/api/research/ethics/project/{id}` | PI, ETHICS_REVIEWER, ETHICS_CHAIR |
| PATCH | `/api/research/ethics/{id}/decision` | ETHICS_CHAIR, ETHICS_REVIEWER |

### Data Capture
| Method | Path | Roles |
|---|---|---|
| GET | `/api/data/forms` | DATA_STEWARD, PI, RESEARCHER |
| POST | `/api/data/forms` | DATA_STEWARD, PI |
| GET | `/api/data/forms/{id}` | DATA_STEWARD, PI |
| POST | `/api/data/forms/{id}/submissions` | RESEARCHER, PI, DATA_STEWARD |
| POST | `/api/data/forms/{id}/upload-csv` | DATA_STEWARD |
| GET | `/api/data/forms/{id}/submissions` | DATA_STEWARD, PI |

### Notifications
| Method | Path | Roles |
|---|---|---|
| GET | `/api/notifications` | Any authenticated |
| PATCH | `/api/notifications/{id}/read` | Any authenticated |

---

## 9. Frontend Routes Map

| Route | Component | Description |
|---|---|---|
| `/login` | existing | Login page |
| `/onboarding` | existing | ORCID onboarding |
| `/global-admin` | existing | Global admin dashboard |
| `/institution-admin` | existing | Institution admin dashboard |
| `/dashboard` | EXTEND | Module tiles + recent activity |
| `/grants` | NEW | Opportunities list |
| `/grants/new` | NEW | Create opportunity form |
| `/grants/[id]` | NEW | Opportunity detail + proposals |
| `/grants/proposals/new` | NEW | Create proposal |
| `/grants/proposals/[id]` | NEW | Proposal workspace (sections, docs) |
| `/review/[id]` | NEW | Reviewer scoring console |
| `/awards/[id]` | NEW | Award detail + budget table |
| `/research` | NEW | Projects list |
| `/research/new` | NEW | Register project |
| `/research/[id]` | NEW | Project workspace |
| `/research/ethics/new` | NEW | Ethics application form |
| `/data` | NEW | Forms list |
| `/data/forms/new` | NEW | Form builder |
| `/data/forms/[id]` | NEW | Form detail + submissions view |
| `/data/upload` | NEW | CSV batch upload |

---

## 10. Demo Scenario Script

Use this script to walk stakeholders through the prototype in ~20 minutes.

### Setup (5 min before demo)
```bash
# Terminal 1
cd backend && python main.py

# Terminal 2
cd frontend && npm run dev

# Verify seed data exists (or run it)
cd backend && python seed.py
```

### Scene 1 — Grant Officer creates an opportunity (2 min)
1. Log in as `grant@demo.ac.ke` / `Demo@12345`
2. Navigate to **Grants** → show existing Digital Health opportunity
3. Click **New Opportunity** → fill in title, sponsor, deadline → Save
4. *Talking point: "This is how new calls for proposals are captured in DACORIS"*

### Scene 2 — PI creates and develops a proposal (4 min)
1. Log out → Log in as `pi@demo.ac.ke` / `Demo@12345`
2. Navigate to **Grants** → click **Apply** on the Digital Health opportunity
3. Name the proposal → system creates the workspace with 5 default sections
4. Fill in Executive Summary section → Save → show completion meter update
5. Upload a PDF document
6. Click **Submit for Internal Review**
7. *Talking point: "Every section is versioned; the completion meter guides the PI"*

### Scene 3 — Grant Officer assigns a reviewer (2 min)
1. Log out → Log in as `grant@demo.ac.ke`
2. Open the submitted proposal
3. Use the API directly (Swagger UI at `:8000/docs`) to assign reviewer_id
4. *Talking point: "In V1.0 this will be a UI action; the workflow engine enforces all stage rules"*

### Scene 4 — Reviewer scores the proposal (3 min)
1. Log out → Log in as `reviewer@demo.ac.ke`
2. Navigate to `/review/1`
3. Declare no COI → score all four criteria using sliders → submit recommendation
4. *Talking point: "COI declaration is enforced — if COI is declared, the scoring form is hidden"*

### Scene 5 — Award issued → Project auto-created (2 min)
1. Log out → Log in as `grant@demo.ac.ke`
2. Use Swagger to call `POST /api/grants/awards` with the proposal_id
3. Log out → Log in as `pi@demo.ac.ke`
4. Navigate to **Research** → show the auto-created project linked to the award
5. *Talking point: "The award_issued event automatically creates a Research project — inter-module workflow in action"*

### Scene 6 — Ethics application (2 min)
1. Still as PI → open the Drought Research project
2. Click **Ethics Application** → fill in the form → Submit
3. Log out → Log in as `ethics@demo.ac.ke`
4. Use Swagger to approve the ethics application
5. *Talking point: "Ethics approval is a gate — data capture cannot begin until it is approved"*

### Scene 7 — Data capture form (3 min)
1. Log out → Log in as `data@demo.ac.ke`
2. Navigate to **Data** → show the pre-seeded Farmer Baseline Survey (KoBoToolbox linked)
3. Click **New Form** → show the form builder — add two fields, save
4. Upload a CSV with sample farmer data
5. Show the submission list with QA status = STAGED
6. *Talking point: "All four capture tools are supported; the QA pipeline is the next build sprint"*

### Scene 8 — Wrap up (2 min)
- Show the Swagger docs at `:8000/docs` — all 25+ endpoints live
- Show the breadth: IAM → Grants → Research → Data in one platform
- Highlight what comes next in V1.0: finance ERP sync, QA automation, DOI minting, public portal

---

## 11. Known Limitations & V1.0 Deferrals

These are deliberate shortcuts made for the prototype. Each item has a V1.0 resolution.

| Prototype Shortcut | V1.0 Resolution |
|---|---|
| Passwords accepted for all users (not ORCID-only) | Enforce ORCID-only for researchers; keep local only for admins |
| File storage on local disk (`./uploads`) | Replace with MinIO (on-prem) / S3 (cloud) via `file_upload.py` swap |
| No actual email notifications (console log only) | Integrate SMTP/SES; Celery Beat for scheduled reminders |
| Reviewer assignment via API (no UI) | Build reviewer assignment UI in grant management console |
| No real KoBoToolbox webhook (form linked by URL only) | Implement webhook endpoint + HMAC verification + Celery consumer |
| QA pipeline is manual (submissions sit at STAGED) | Build automated QA rule engine (missing values, duplicates, range checks) |
| No document viewer (download only) | PDF preview via embedded viewer |
| No real-time collaboration (sections save one at a time) | Implement optimistic concurrency, conflict detection |
| No audit log UI | Build audit trail viewer in admin panel |
| Budget lines have no expense tracking | Build expense report submission + ERP sync connectors |
| Ethics workflow has no reviewer assignment UI | Build ethics committee management UI |
| No public portal | Build Next.js public-facing portal (unauthenticated) |
| No Data Part B (analytics) | Entire Phase 4 |
| `has_role()` method on User not yet implemented | Add helper method to User model using `user_roles` table |
| No pagination on list endpoints | Add `skip` / `limit` query params and total count headers |
| CORS allows only localhost:3000 | Configure per-environment allowed origins |

---

## 12. Prototype Checklist

### Backend
- [ ] All new dependencies installed and in `requirements.txt`
- [ ] Alembic configured and migrations applied
- [ ] All models appended to `models.py` (no existing models touched)
- [ ] All route files created with `__init__.py` in each directory
- [ ] All routers included in `main.py`
- [ ] Services created: `workflow.py`, `notifications.py`, `file_upload.py`
- [ ] `./uploads/documents` directory created
- [ ] Seed script runs without errors
- [ ] All 25+ endpoints visible at `http://localhost:8000/docs`
- [ ] Health check passes: `GET /api/health`

### Frontend
- [ ] All new npm packages installed
- [ ] `apiModules.js` created with all module API calls
- [ ] `AppShell.js` layout with working sidebar navigation
- [ ] Grants pages: opportunities list, proposal workspace, review console
- [ ] Research pages: projects list, project detail, ethics form
- [ ] Data pages: forms list, form builder, submission view
- [ ] All pages use `AppShell` for consistent layout
- [ ] Auth guard present on all protected pages (redirect to `/login` if no token)
- [ ] Error and loading states handled on all data-fetching pages

### Demo Ready
- [ ] Seed data loaded with demo institution and 6 user accounts
- [ ] End-to-end scenario completes without errors:
  - [ ] Create opportunity
  - [ ] Create proposal with sections
  - [ ] Upload document
  - [ ] Submit for review
  - [ ] Submit review scores
  - [ ] Issue award
  - [ ] Research project auto-created
  - [ ] Submit ethics application
  - [ ] Create capture form
  - [ ] Upload CSV submissions
- [ ] Both servers running (`backend :8000`, `frontend :3000`)
- [ ] Swagger docs accessible at `http://localhost:8000/docs`
- [ ] Demo credentials tested: all 6 user logins work

---

*Prototype target: functional demonstration within 2 weeks. Focus is end-to-end scenario coverage, not completeness. Every shortcut listed in Section 11 has a defined resolution path in the full implementation plan (v1.3).*
