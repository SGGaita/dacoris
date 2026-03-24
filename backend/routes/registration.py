"""
Registration routes for multi-step account creation
Supports both ORCID-based and email-based registration flows
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import json

from database import get_db
from models import User, Institution, AccountType, UserStatus, PrimaryAccountType
from account_types import (
    get_self_registration_account_types,
    validate_account_type_for_registration,
    requires_orcid,
    get_default_roles
)
from auth import get_password_hash
import sys
sys.path.append('..')

router = APIRouter(prefix="/api/registration", tags=["registration"])


class AccountTypeInfo(BaseModel):
    value: str
    label: str
    description: str
    requires_orcid: bool
    icon: str


class RegistrationStep1Request(BaseModel):
    """Step 1: Select account type"""
    account_type: str
    
    @validator('account_type')
    def validate_account_type(cls, v):
        account_type_enum = validate_account_type_for_registration(v)
        if not account_type_enum:
            raise ValueError('Invalid account type or invitation-only account type')
        return v


class RegistrationStep2OrcidRequest(BaseModel):
    """Step 2: ORCID authentication (for ORCID-required accounts)"""
    account_type: str
    orcid_id: str
    orcid_access_token: str
    orcid_refresh_token: Optional[str] = None
    orcid_token_expires_at: Optional[datetime] = None


class RegistrationStep3DetailsRequest(BaseModel):
    """Step 3: Account details"""
    account_type: str
    orcid_id: Optional[str] = None
    name: str
    email: EmailStr
    institution_domain: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    expertise_keywords: Optional[List[str]] = None


class RegistrationStep4PasswordRequest(BaseModel):
    """Step 4: Password setup and final submission"""
    account_type: str
    orcid_id: Optional[str] = None
    name: str
    email: EmailStr
    institution_domain: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    expertise_keywords: Optional[List[str]] = None
    password: str
    confirm_password: str
    accept_terms: bool
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('accept_terms')
    def terms_accepted(cls, v):
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v


class RegistrationResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    status: Optional[str] = None
    requires_approval: bool = True


@router.get("/account-types", response_model=List[AccountTypeInfo])
async def get_account_types():
    """Get list of available account types for self-registration"""
    return get_self_registration_account_types()


@router.post("/validate-step1")
async def validate_step1(request: RegistrationStep1Request):
    """Validate account type selection"""
    account_type_enum = validate_account_type_for_registration(request.account_type)
    if not account_type_enum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account type"
        )
    
    return {
        "valid": True,
        "requires_orcid": requires_orcid(account_type_enum),
        "account_type": request.account_type
    }


@router.post("/validate-email")
async def validate_email(
    email: EmailStr,
    institution_domain: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate email and check institution domain"""
    # Extract domain from email
    email_domain = email.split('@')[1].lower()
    
    # Find institution by domain
    result = await db.execute(
        select(Institution).where(Institution.domain == institution_domain.lower())
    )
    institution = result.scalar_one_or_none()
    
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    
    # Check if email domain matches institution domain
    valid_domains = [institution.domain.lower()]
    if institution.verified_domains:
        valid_domains.extend([d.strip().lower() for d in institution.verified_domains.split(',')])
    
    if email_domain not in valid_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email domain must match institution domain ({', '.join(valid_domains)})"
        )
    
    # Check if email already exists for this institution
    result = await db.execute(
        select(User).where(
            User.email == email.lower(),
            User.primary_institution_id == institution.id
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists for this institution"
        )
    
    return {
        "valid": True,
        "institution_id": institution.id,
        "institution_name": institution.name
    }


@router.post("/complete", response_model=RegistrationResponse)
async def complete_registration(
    request: RegistrationStep4PasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Complete registration and create user account"""
    
    # Validate account type
    account_type_enum = validate_account_type_for_registration(request.account_type)
    if not account_type_enum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account type"
        )
    
    # Check ORCID requirement
    if requires_orcid(account_type_enum) and not request.orcid_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ORCID authentication is required for this account type"
        )
    
    # Find institution
    result = await db.execute(
        select(Institution).where(Institution.domain == request.institution_domain.lower())
    )
    institution = result.scalar_one_or_none()
    
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    
    # Validate email domain
    email_domain = request.email.split('@')[1].lower()
    valid_domains = [institution.domain.lower()]
    if institution.verified_domains:
        valid_domains.extend([d.strip().lower() for d in institution.verified_domains.split(',')])
    
    if email_domain not in valid_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email domain must match institution domain"
        )
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            User.email == request.email.lower(),
            User.primary_institution_id == institution.id
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # Check if ORCID already exists (if provided)
    if request.orcid_id:
        result = await db.execute(
            select(User).where(User.orcid_id == request.orcid_id)
        )
        existing_orcid_user = result.scalar_one_or_none()
        
        if existing_orcid_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this ORCID iD already exists"
            )
    
    # Create user account
    new_user = User(
        email=request.email.lower(),
        name=request.name,
        password_hash=get_password_hash(request.password),
        account_type=AccountType.ORCID if request.orcid_id else AccountType.INSTITUTION_ADMIN,
        status=UserStatus.PENDING,
        orcid_id=request.orcid_id,
        primary_institution_id=institution.id,
        primary_account_type=account_type_enum,
        department=request.department,
        job_title=request.job_title,
        phone=request.phone,
        expertise_keywords=json.dumps(request.expertise_keywords) if request.expertise_keywords else None,
        is_global_admin=False,
        is_institution_admin=False,
        is_guest=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Assign default role based on account type
    default_roles = get_default_roles(account_type_enum)
    if default_roles:
        from sqlalchemy import insert
        from models import user_roles
        
        for role in default_roles:
            await db.execute(
                insert(user_roles).values(
                    user_id=new_user.id,
                    role=role,
                    assigned_by=None
                )
            )
        await db.commit()
    
    return RegistrationResponse(
        success=True,
        message="Registration successful. Your account is pending approval by your institution administrator.",
        user_id=new_user.id,
        status=new_user.status.value,
        requires_approval=True
    )


@router.get("/departments/{institution_domain}")
async def get_departments(
    institution_domain: str,
    db: AsyncSession = Depends(get_db)
):
    """Get list of departments for an institution (placeholder - to be implemented)"""
    # This would query a Department table when implemented
    # For now, return common departments
    return {
        "departments": [
            "Faculty of Science",
            "Faculty of Arts",
            "Faculty of Engineering",
            "Faculty of Medicine",
            "Faculty of Business",
            "Faculty of Law",
            "Faculty of Education",
            "Research Administration",
            "Finance Department",
            "IT Department",
            "Other"
        ]
    }
