import cloudinary
import cloudinary.uploader
from src.conf.config import settings
from fastapi import UploadFile
import uuid

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.cloudinary_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret
        )

    async def upload_avatar(self, file: UploadFile, user_id: int):
        """
        Upload avatar to Cloudinary
        :param file: Uploaded file
        :param user_id: User ID for unique filename
        :return: Cloudinary URL of uploaded image
        """
        # Generate a unique filename
        filename = f"avatar_{user_id}_{uuid.uuid4()}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content, 
            public_id=filename,
            folder="avatars",
            overwrite=True,
            resource_type="image"
        )
        
        return upload_result['secure_url']

cloudinary_service = CloudinaryService()