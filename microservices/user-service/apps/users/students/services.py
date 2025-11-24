from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from shared.shared.utils.prisma_client import get_prisma_client, disconnect_prisma
import logging
import random
import string

logger = logging.getLogger(__name__)


class StudentService:
    """Service pour gérer les étudiants"""
    
    def __init__(self):
        self.db = None
    
    async def connect(self):
        """Connexion via singleton"""
        self.db = await get_prisma_client()
    
    async def disconnect(self):
        """Ne plus déconnecter individuellement"""
        pass  # Géré par le singleton
    
    def generate_student_code(self) -> str:
        """Générer un code étudiant unique"""
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"STU{year}{random_part}"
    
    async def create_student(self, user_id: str, data: Dict[str, Any] = None) -> dict:
        """Créer un nouveau profil étudiant"""
        try:
            await self.connect()
            
            # Générer un code étudiant unique
            student_code = self.generate_student_code()
            
            # Vérifier l'unicité avec retry
            max_retries = 5
            for _ in range(max_retries):
                existing = await self.db.student.find_unique(
                    where={'studentCode': student_code}
                )
                if not existing:
                    break
                student_code = self.generate_student_code()
            
            student_data = {
                'userId': user_id,
                'studentCode': student_code,
                'points': data.get('points', 0) if data else 0,
                'level': data.get('level', 1) if data else 1,
                'experiencePoints': data.get('experience_points', 0) if data else 0,
                'streak': 0,
                'maxStreak': 0,
                'totalCoursesEnrolled': 0,
                'totalCoursesCompleted': 0,
                'totalLearningTime': 0,
                'totalCertificates': 0,
                'preferredCategories': data.get('preferred_categories', []) if data else [],
            }
            
            student = await self.db.student.create(data=student_data)
            
            logger.info(f"Student created for user: {user_id} with code: {student_code}")
            return student

        except Exception as e:
            logger.error(f"Error creating student: {str(e)}", exc_info=True)
            raise
        finally:
            await self.disconnect()
    
    async def get_student(self, user_id: str) -> Optional[dict]:
        """Récupérer le profil étudiant"""
        try:
            await self.connect()
            return await self.db.student.find_unique(where={'userId': user_id})
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'étudiant: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def get_student_by_code(self, student_code: str) -> Optional[dict]:
        """Récupérer un étudiant par son code"""
        try:
            await self.connect()
            return await self.db.student.find_unique(where={'studentCode': student_code})
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'étudiant par code: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def update_student(self, user_id: str, data: Dict[str, Any]) -> Optional[dict]:
        """Mettre à jour le profil étudiant"""
        try:
            await self.connect()
            
            update_data = {}
            field_mapping = {
                'points': 'points',
                'level': 'level',
                'experience_points': 'experiencePoints',
                'streak': 'streak',
                'max_streak': 'maxStreak',
                'last_activity_date': 'lastActivityDate',
                'total_courses_enrolled': 'totalCoursesEnrolled',
                'total_courses_completed': 'totalCoursesCompleted',
                'total_learning_time': 'totalLearningTime',
                'total_certificates': 'totalCertificates',
                'preferred_categories': 'preferredCategories',
            }
            
            for key, prisma_key in field_mapping.items():
                if key in data:
                    update_data[prisma_key] = data[key]
            
            if not update_data:
                return await self.get_student(user_id)
            
            student = await self.db.student.update(
                where={'userId': user_id},
                data=update_data
            )
            
            logger.info(f"Étudiant mis à jour pour l'utilisateur: {user_id}")
            return student

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'étudiant: {str(e)}")
            raise
        finally:
            await self.disconnect()
    
    async def add_experience_points(self, user_id: str, points: int) -> Optional[dict]:
        """Ajouter des points d'expérience et gérer le niveau"""
        try:
            await self.connect()
            
            student = await self.get_student(user_id)
            if not student:
                return None
            
            new_xp = student.experiencePoints + points
            new_level = self.calculate_level(new_xp)
            
            return await self.update_student(user_id, {
                'experience_points': new_xp,
                'level': new_level,
                'points': student.points + (points // 10),  # 1 point pour 10 XP
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'XP: {str(e)}")
            raise
    
    def calculate_level(self, xp: int) -> int:
        """Calculer le niveau basé sur l'XP (100 XP par niveau)"""
        return max(1, (xp // 100) + 1)
    
    async def update_streak(self, user_id: str) -> Optional[dict]:
        """Mettre à jour le streak d'activité"""
        try:
            await self.connect()
            
            student = await self.get_student(user_id)
            if not student:
                return None
            
            today = datetime.now().date()
            last_activity = student.lastActivityDate.date() if student.lastActivityDate else None
            
            if last_activity is None:
                new_streak = 1
            elif last_activity == today:
                return student
            elif last_activity == today - timedelta(days=1):
                new_streak = student.streak + 1
            else:
                new_streak = 1
            
            max_streak = max(student.maxStreak, new_streak)
            
            return await self.update_student(user_id, {
                'streak': new_streak,
                'max_streak': max_streak,
                'last_activity_date': datetime.now(),
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du streak: {str(e)}")
            raise
    
    async def enroll_course(self, user_id: str) -> Optional[dict]:
        """Incrémenter le nombre de cours inscrits"""
        try:
            student = await self.get_student(user_id)
            if not student:
                return None
            
            return await self.update_student(user_id, {
                'total_courses_enrolled': student.totalCoursesEnrolled + 1
            })
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription au cours: {str(e)}")
            raise
    
    async def complete_course(self, user_id: str, learning_time: int = 0) -> Optional[dict]:
        """Marquer un cours comme complété"""
        try:
            student = await self.get_student(user_id)
            if not student:
                return None
            
            return await self.update_student(user_id, {
                'total_courses_completed': student.totalCoursesCompleted + 1,
                'total_learning_time': student.totalLearningTime + learning_time,
            })
        except Exception as e:
            logger.error(f"Erreur lors de la completion du cours: {str(e)}")
            raise
    
    async def get_leaderboard(self, limit: int = 10) -> List[dict]:
        """Récupérer le classement des meilleurs étudiants"""
        try:
            await self.connect()
            
            students = await self.db.student.find_many(
                order={'points': 'desc'},
                take=limit
            )
            
            return students
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du classement: {str(e)}")
            raise
        finally:
            await self.disconnect()
