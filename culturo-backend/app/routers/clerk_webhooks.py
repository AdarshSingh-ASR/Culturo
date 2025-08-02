"""
Clerk webhook handlers for user synchronization
"""
from fastapi import APIRouter, Request, HTTPException, Depends
import hmac
import hashlib
import json
from typing import Dict, Any

from ..database import get_db
from ..config import settings

router = APIRouter()


def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """Verify Clerk webhook signature"""
    if not settings.clerk_webhook_secret:
        return False
    
    expected_signature = hmac.new(
        settings.clerk_webhook_secret.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"v1={expected_signature}", signature)


@router.post("/webhook")
async def clerk_webhook(
    request: Request,
    db = Depends(get_db)
):
    """Handle Clerk webhook events"""
    # Get the raw body
    body = await request.body()
    
    # Verify webhook signature
    signature = request.headers.get("svix-signature")
    if not signature or not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Parse the webhook data
    try:
        webhook_data = json.loads(body)
        event_type = webhook_data.get("type")
        data = webhook_data.get("data", {})
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Handle different event types
    if event_type == "user.created":
        await handle_user_created(data, db)
    elif event_type == "user.updated":
        await handle_user_updated(data, db)
    elif event_type == "user.deleted":
        await handle_user_deleted(data, db)
    else:
        # Log unhandled event types
        print(f"Unhandled webhook event: {event_type}")
    
    return {"status": "success"}


async def handle_user_created(data: Dict[Any, Any], db):
    """Handle user.created webhook event"""
    user_data = data.get("user", {})
    clerk_id = user_data.get("id")
    
    if not clerk_id:
        return
    
    # Check if user already exists
    existing_user = db.user.find_first(where={"clerk_id": clerk_id})
    if existing_user:
        return
    
    # Create new user
    email = user_data.get("email_addresses", [{}])[0].get("email_address") if user_data.get("email_addresses") else None
    
    user = db.user.create(
        data={
            "clerk_id": clerk_id,
            "email": email,
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "username": user_data.get("username"),
            "profile_image_url": user_data.get("image_url"),
            "full_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            "is_active": True,
            "is_verified": user_data.get("email_addresses", [{}])[0].get("verification", {}).get("status") == "verified"
        }
    )


async def handle_user_updated(data: Dict[Any, Any], db):
    """Handle user.updated webhook event"""
    user_data = data.get("user", {})
    clerk_id = user_data.get("id")
    
    if not clerk_id:
        return
    
    # Find existing user
    user = db.user.find_first(where={"clerk_id": clerk_id})
    if not user:
        return
    
    # Update user data
    email = user_data.get("email_addresses", [{}])[0].get("email_address") if user_data.get("email_addresses") else None
    
    db.user.update(
        where={"clerk_id": clerk_id},
        data={
            "email": email,
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "username": user_data.get("username"),
            "profile_image_url": user_data.get("image_url"),
            "full_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            "is_verified": user_data.get("email_addresses", [{}])[0].get("verification", {}).get("status") == "verified"
        }
    )


async def handle_user_deleted(data: Dict[Any, Any], db):
    """Handle user.deleted webhook event"""
    user_data = data.get("user", {})
    clerk_id = user_data.get("id")
    
    if not clerk_id:
        return
    
    # Find and deactivate user
    user = db.user.find_first(where={"clerk_id": clerk_id})
    if user:
        db.user.update(
            where={"clerk_id": clerk_id},
            data={"is_active": False}
        ) 