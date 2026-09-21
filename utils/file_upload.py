import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, status, UploadFile

BASE_UPLOAD_DIR = "static/uploads"


def save_upload_image(
    file: UploadFile, 
    upload_subfolder: str = "general"
) -> Optional[str]:

    if not file.content_type or not file.content_type.startswith("image/"):
        return None

    try:
        target_dir = os.path.join(BASE_UPLOAD_DIR, upload_subfolder)
        os.makedirs(target_dir, exist_ok=True)

        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(target_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return f"/{file_path.replace('\\', '/')}"
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving image to server storage"
        ) from e


def save_multiple_images(
    images: Optional[List[UploadFile]], 
    upload_subfolder: str = "general"
) -> List[str]:

    if not images:
        return []

    saved_urls: List[str] = []
    for file in images:
        image_url = save_upload_image(file, upload_subfolder=upload_subfolder)
        if image_url:
            saved_urls.append(image_url)

    return saved_urls