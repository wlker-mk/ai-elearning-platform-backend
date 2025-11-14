from typing import Optional, Dict, Any
from datetime import datetime
from prisma import Prisma
import logging

logger = logging.getLogger(__name__)


class ProfileService:
    """Service pour gérer les profils utilisateurs"""

    def __init__(self):
        self.db = Prisma()

    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()

    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()

    async def create_profile(self, user_id: str, data: Dict[str, Any]) -> dict:
        try:
            await self.connect()

            profile = await self.db.userprofile.create(
                data={
                    'userId': user_id,
                    'firstName': data.get('first_name'),
                    'lastName': data.get('last_name'),
                    'phoneNumber': data.get('phone_number'),
                    'dateOfBirth': data.get('date_of_birth'),
                    'profileImageUrl': data.get('profile_image_url'),
                    'coverImageUrl': data.get('cover_image_url'),
                    'bio': data.get('bio'),
                    'website': data.get('website'),
                    'linkedin': data.get('linkedin'),
                    'github': data.get('github'),
                    'twitter': data.get('twitter'),
                    'facebook': data.get('facebook'),
                    'country': data.get('country'),
                    'city': data.get('city'),
                    'timezone': data.get('timezone', 'UTC'),
                    'language': data.get('language', 'en'),
                }
            )

            logger.info(f"Profile created for user: {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def get_profile(self, user_id: str) -> Optional[dict]:
        try:
            await self.connect()

            return await self.db.userprofile.find_unique(
                where={'userId': user_id}
            )

        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def update_profile(self, user_id: str, data: Dict[str, Any]) -> Optional[dict]:
        try:
            await self.connect()

            update_data = {}
            field_mapping = {
                'first_name': 'firstName',
                'last_name': 'lastName',
                'phone_number': 'phoneNumber',
                'date_of_birth': 'dateOfBirth',
                'profile_image_url': 'profileImageUrl',
                'cover_image_url': 'coverImageUrl',
                'bio': 'bio',
                'website': 'website',
                'linkedin': 'linkedin',
                'github': 'github',
                'twitter': 'twitter',
                'facebook': 'facebook',
                'country': 'country',
                'city': 'city',
                'timezone': 'timezone',
                'language': 'language',
            }

            for key, prisma_key in field_mapping.items():
                if key in data:
                    update_data[prisma_key] = data[key]

            if not update_data:
                return await self.get_profile(user_id)

            profile = await self.db.userprofile.update(
                where={'userId': user_id},
                data=update_data
            )

            logger.info(f"Profile updated for user: {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def delete_profile(self, user_id: str) -> bool:
        try:
            await self.connect()

            await self.db.userprofile.delete(
                where={'userId': user_id}
            )

            logger.info(f"Profile deleted for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            raise
        finally:
            await self.disconnect()