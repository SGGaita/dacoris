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
        ResearchRole.GRANT_OFFICER, ResearchRole.PRINCIPAL_INVESTIGATOR,
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
        ResearchRole.GRANT_OFFICER, ResearchRole.PRINCIPAL_INVESTIGATOR,
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
