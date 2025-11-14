from typing import Optional, Dict, Any, List
from datetime import datetime
from prisma import Prisma
import logging
import random
import string

logger = logging.getLogger(__name__)


class InstructorService:
    """Service pour gérer les instructeurs"""

    def __init__(self):
        self.db = Prisma()

    async def connect(self):
        if not self.db.is_connected():
            await self.db.connect()

    async def disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()

    def generate_instructor_code(self) -> str:
        """Générer un code instructeur unique"""
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"INS{year}{random_part}"

    async def create_instructor(self, user_id: str, data: Dict[str, Any]) -> dict:
        """Créer un nouveau profil instructeur"""
        try:
            await self.connect()

            # Générer un code instructeur unique
            instructor_code = self.generate_instructor_code()

            # Vérifier l'unicité
            while await self.db.instructor.find_unique(where={'instructorCode': instructor_code}):
                instructor_code = self.generate_instructor_code()

            instructor_data = {
                'userId': user_id,
                'instructorCode': instructor_code,
                'title': data.get('title'),
                'headline': data.get('headline'),
                'specializations': data.get('specializations', []),
                'expertise': data.get('expertise', []),
                'certifications': data.get('certifications', []),
                'yearsOfExperience': data.get('years_of_experience', 0),
                'hourlyRate': data.get('hourly_rate'),
                'rating': 0.0,
                'totalReviews': 0,
                'totalStudents': 0,
                'totalCourses': 0,
                'isVerified': False,
                'bankAccount': data.get('bank_account'),
                'bankName': data.get('bank_name'),
                'paypalEmail': data.get('paypal_email'),
            }

            instructor = await self.db.instructor.create(data=instructor_data)

            logger.info(f"Instructor created for user: {user_id} with code: {instructor_code}")
            return instructor

        except Exception as e:
            logger.error(f"Error creating instructor: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def get_instructor(self, user_id: str) -> Optional[dict]:
        """Récupérer le profil instructeur"""
        try:
            await self.connect()
            return await self.db.instructor.find_unique(where={'userId': user_id})
        except Exception as e:
            logger.error(f"Error fetching instructor: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def get_instructor_by_code(self, instructor_code: str) -> Optional[dict]:
        """Récupérer un instructeur par son code"""
        try:
            await self.connect()
            return await self.db.instructor.find_unique(where={'instructorCode': instructor_code})
        except Exception as e:
            logger.error(f"Error fetching instructor by code: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def update_instructor(self, user_id: str, data: Dict[str, Any]) -> Optional[dict]:
        """Mettre à jour le profil instructeur"""
        try:
            await self.connect()

            update_data = {}
            field_mapping = {
                'title': 'title',
                'headline': 'headline',
                'specializations': 'specializations',
                'expertise': 'expertise',
                'certifications': 'certifications',
                'years_of_experience': 'yearsOfExperience',
                'hourly_rate': 'hourlyRate',
                'bank_account': 'bankAccount',
                'bank_name': 'bankName',
                'paypal_email': 'paypalEmail',
            }

            for key, prisma_key in field_mapping.items():
                if key in data:
                    update_data[prisma_key] = data[key]

            if not update_data:
                return await self.get_instructor(user_id)

            instructor = await self.db.instructor.update(
                where={'userId': user_id},
                data=update_data
            )

            logger.info(f"Instructor updated for user: {user_id}")
            return instructor

        except Exception as e:
            logger.error(f"Error updating instructor: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def verify_instructor(self, user_id: str) -> Optional[dict]:
        """Vérifier un instructeur"""
        try:
            await self.connect()

            instructor = await self.db.instructor.update(
                where={'userId': user_id},
                data={
                    'isVerified': True,
                    'verifiedAt': datetime.now()
                }
            )

            logger.info(f"Instructor verified: {user_id}")
            return instructor

        except Exception as e:
            logger.error(f"Error verifying instructor: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def unverify_instructor(self, user_id: str) -> Optional[dict]:
        """Retirer la vérification d'un instructeur"""
        try:
            await self.connect()

            instructor = await self.db.instructor.update(
                where={'userId': user_id},
                data={
                    'isVerified': False,
                    'verifiedAt': None
                }
            )

            logger.info(f"Instructor unverified: {user_id}")
            return instructor

        except Exception as e:
            logger.error(f"Error unverifying instructor: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def update_rating(self, user_id: str, new_rating: float) -> Optional[dict]:
        """Mettre à jour la note"""
        try:
            await self.connect()

            instructor = await self.get_instructor(user_id)
            if not instructor:
                return None

            total_reviews = instructor['totalReviews']
            current_rating = instructor['rating'] or 0.0

            new_total = total_reviews + 1
            new_avg = ((current_rating * total_reviews) + new_rating) / new_total

            updated_instructor = await self.db.instructor.update(
                where={'userId': user_id},
                data={
                    'rating': round(new_avg, 2),
                    'totalReviews': new_total
                }
            )

            logger.info(f"Rating updated for instructor: {user_id}")
            return updated_instructor

        except Exception as e:
            logger.error(f"Error updating rating: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def increment_students(self, user_id: str, count: int = 1) -> Optional[dict]:
        try:
            instructor = await self.get_instructor(user_id)
            if not instructor:
                return None

            return await self.db.instructor.update(
                where={'userId': user_id},
                data={'totalStudents': instructor['totalStudents'] + count}
            )
        except Exception as e:
            logger.error(f"Error incrementing students: {str(e)}")
            raise

    async def increment_courses(self, user_id: str, count: int = 1) -> Optional[dict]:
        try:
            instructor = await self.get_instructor(user_id)
            if not instructor:
                return None

            return await self.db.instructor.update(
                where={'userId': user_id},
                data={'totalCourses': instructor['totalCourses'] + count}
            )
        except Exception as e:
            logger.error(f"Error incrementing courses: {str(e)}")
            raise

    async def get_top_instructors(self, limit: int = 10) -> List[dict]:
        try:
            await self.connect()

            return await self.db.instructor.find_many(
                where={'isVerified': True},
                order=[
                    {'rating': 'desc'},
                    {'totalStudents': 'desc'}
                ],
                take=limit
            )

        except Exception as e:
            logger.error(f"Error fetching top instructors: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def search_instructors(
        self,
        specialization: Optional[str] = None,
        min_rating: Optional[float] = None,
        verified_only: bool = False,
        limit: int = 20
    ) -> List[dict]:
        try:
            await self.connect()

            where = {}

            if verified_only:
                where['isVerified'] = True
            if min_rating is not None:
                where['rating'] = {'gte': min_rating}
            if specialization:
                where['specializations'] = {'has': specialization}

            return await self.db.instructor.find_many(
                where=where,
                order={'rating': 'desc'},
                take=limit
            )

        except Exception as e:
            logger.error(f"Error searching instructors: {str(e)}")
            raise
        finally:
            await self.disconnect()
