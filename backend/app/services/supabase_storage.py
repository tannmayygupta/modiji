import os
import uuid
from supabase import create_client, Client
from app.config import get_settings

def get_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_file_to_supabase(file_bytes: bytes, file_name: str, bucket_name: str, folder_name: str, content_type: str) -> str | None:
    """
    Uploads a file to Supabase Storage and returns the public URL.
    Generates a unique sub-path using uuid to prevent collisions.
    """
    soup_client = get_supabase_client()
    if not soup_client:
        return None
    
    unique_path = f"{folder_name}/{uuid.uuid4().hex[:8]}_{file_name}"
    
    # Upload to Supabase Storage
    try:
        res = soup_client.storage.from_(bucket_name).upload(
            file=file_bytes,
            path=unique_path,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        
        # Get public url
        public_url = soup_client.storage.from_(bucket_name).get_public_url(unique_path)
        return public_url
    except Exception as e:
        error_msg = str(e)
        if "row-level security" in error_msg.lower() or "403" in error_msg:
             raise ValueError("Supabase RLS Error: Your bucket is private. Go to Supabase Dashboard -> Storage -> pmis-media -> Policies, and allow INSERT/SELECT for Public!")
        raise ValueError(f"SDK Error: {error_msg}")
