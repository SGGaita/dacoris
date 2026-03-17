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
    current_user: User = Depends(require_roles([ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.GRANT_OFFICER]))
):
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
    await db.flush()

    for s in DEFAULT_SECTIONS:
        db.add(ProposalSection(proposal_id=proposal.id, **s))

    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.get("", response_model=List[ProposalOut])
async def list_proposals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.GRANT_OFFICER,
        ResearchRole.INSTITUTIONAL_LEAD
    ]))
):
    query = select(Proposal).where(
        Proposal.institution_id == current_user.primary_institution_id
    )
    result = await db.execute(query.order_by(Proposal.created_at.desc()))
    return result.scalars().all()


@router.get("/{proposal_id}")
async def get_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([
        ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.GRANT_OFFICER,
        ResearchRole.INSTITUTIONAL_LEAD
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
    current_user: User = Depends(require_roles([ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.GRANT_OFFICER]))
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
    current_user: User = Depends(require_roles([ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.GRANT_OFFICER]))
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
        ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.GRANT_OFFICER
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

    if target_status == ProposalStatus.RETURNED and proposal.lead_pi_id != current_user.id:
        await create_notification(
            db, proposal.lead_pi_id,
            title="Proposal returned for revision",
            message=f'Your proposal "{proposal.title}" requires revision.',
            entity_type="proposal", entity_id=proposal_id
        )

    return {"id": proposal_id, "status": target_status}
