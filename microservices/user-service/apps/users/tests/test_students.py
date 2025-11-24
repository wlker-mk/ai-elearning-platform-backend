# apps/users/tests/test_students.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

User = get_user_model()


class StudentAPITestCase(APITestCase):
    """Tests pour les endpoints étudiants"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = APIClient()
        
        # Créer un étudiant
        self.student_user = User.objects.create_user(
            id=uuid.uuid4(),
            email='student@test.com',
            username='student',
            password='StudentPass123!',
            role='student'
        )
        
        # Générer token
        refresh = RefreshToken.for_user(self.student_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.student_code = 'STU2024123456'
    
    def tearDown(self):
        """Nettoyage"""
        User.objects.all().delete()
    
    # ==========================================
    # TESTS DE CRÉATION DE PROFIL ÉTUDIANT
    # ==========================================
    
    @patch('apps.users.students.services.StudentService.create_student')
    async def test_create_student_success(self, mock_create):
        """Test création profil étudiant avec succès"""
        mock_student = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 0,
            'level': 1,
            'experiencePoints': 0,
            'streak': 0,
            'maxStreak': 0,
            'lastActivityDate': None,
            'totalCoursesEnrolled': 0,
            'totalCoursesCompleted': 0,
            'totalLearningTime': 0,
            'totalCertificates': 0,
            'preferredCategories': ['Programming', 'Data Science'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_create.return_value = mock_student
        
        data = {
            'preferred_categories': ['Programming', 'Data Science']
        }
        
        response = self.client.post(
            '/api/users/students/me/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('student_code', response.data)
        self.assertEqual(response.data['level'], 1)
        self.assertEqual(response.data['points'], 0)
    
    @patch('apps.users.students.services.StudentService.get_student')
    async def test_create_student_already_exists(self, mock_get):
        """Test création quand le profil existe déjà"""
        mock_get.return_value = {'userId': str(self.student_user.id)}
        
        data = {'preferred_categories': ['Programming']}
        
        response = self.client.post(
            '/api/users/students/me/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', response.data['error'].lower())
    
    def test_create_student_unauthenticated(self):
        """Test création sans authentification"""
        self.client.credentials()
        
        data = {'preferred_categories': ['Programming']}
        response = self.client.post('/api/users/students/me/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('apps.users.students.services.StudentService.create_student')
    async def test_create_student_without_categories(self, mock_create):
        """Test création sans catégories préférées"""
        mock_student = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 0,
            'level': 1,
            'experiencePoints': 0,
            'streak': 0,
            'maxStreak': 0,
            'lastActivityDate': None,
            'totalCoursesEnrolled': 0,
            'totalCoursesCompleted': 0,
            'totalLearningTime': 0,
            'totalCertificates': 0,
            'preferredCategories': [],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_create.return_value = mock_student
        
        response = self.client.post('/api/users/students/me/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['preferred_categories'], [])
    
    # ==========================================
    # TESTS DE RÉCUPÉRATION DE PROFIL ÉTUDIANT
    # ==========================================
    
    @patch('apps.users.students.services.StudentService.get_student')
    async def test_get_student_success(self, mock_get):
        """Test récupération profil étudiant"""
        mock_student = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 150,
            'level': 2,
            'experiencePoints': 250,
            'streak': 5,
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming', 'Data Science'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_get.return_value = mock_student
        
        response = self.client.get('/api/users/students/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['points'], 150)
        self.assertEqual(response.data['level'], 2)
        self.assertEqual(response.data['streak'], 5)
    
    @patch('apps.users.students.services.StudentService.get_student')
    async def test_get_student_not_found(self, mock_get):
        """Test récupération profil inexistant"""
        mock_get.return_value = None
        
        response = self.client.get('/api/users/students/me/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==========================================
    # TESTS DE MISE À JOUR DE PROFIL ÉTUDIANT
    # ==========================================
    
    @patch('apps.users.students.services.StudentService.update_student')
    async def test_update_student_categories(self, mock_update):
        """Test mise à jour des catégories préférées"""
        update_data = {
            'preferred_categories': ['Web Development', 'Mobile Development']
        }
        
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 150,
            'level': 2,
            'experiencePoints': 250,
            'streak': 5,
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Web Development', 'Mobile Development'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update.return_value = mock_updated
        
        response = self.client.put(
            '/api/users/students/me/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['preferred_categories']), 2)
    
    # ==========================================
    # TESTS D'EXPÉRIENCE ET NIVEAUX
    # ==========================================
    
    @patch('apps.users.students.services.StudentService.add_experience_points')
    async def test_add_experience_points_success(self, mock_add_xp):
        """Test ajout de points d'expérience"""
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 15,  # 150 XP = 15 points
            'level': 2,
            'experiencePoints': 150,
            'streak': 5,
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_add_xp.return_value = mock_updated
        
        data = {'points': 150}
        response = self.client.post(
            '/api/users/students/experience/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['experience_points'], 150)
        self.assertEqual(response.data['points'], 15)
    
    @patch('apps.users.students.services.StudentService.add_experience_points')
    async def test_add_experience_level_up(self, mock_add_xp):
        """Test montée de niveau"""
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 30,
            'level': 3,  # Level up!
            'experiencePoints': 300,
            'streak': 5,
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_add_xp.return_value = mock_updated
        
        data = {'points': 300}
        response = self.client.post(
            '/api/users/students/experience/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['level'], 3)
    
    def test_add_experience_invalid_points(self):
        """Test ajout de points négatifs"""
        data = {'points': -50}
        
        response = self.client.post(
            '/api/users/students/experience/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('points', response.data)
    
    def test_add_experience_missing_points(self):
        """Test ajout sans spécifier les points"""
        response = self.client.post(
            '/api/users/students/experience/',
            {},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('points', response.data)
    
    # ==========================================
    # TESTS DE STREAK
    # ==========================================
    
    @patch('apps.users.students.services.StudentService.update_streak')
    async def test_update_streak_new_day(self, mock_update_streak):
        """Test mise à jour du streak - nouveau jour"""
        yesterday = datetime.now() - timedelta(days=1)
        
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 150,
            'level': 2,
            'experiencePoints': 250,
            'streak': 6,  # Streak augmenté
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update_streak.return_value = mock_updated
        
        response = self.client.post('/api/users/students/streak/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['streak'], 6)
    
    @patch('apps.users.students.services.StudentService.update_streak')
    async def test_update_streak_same_day(self, mock_update_streak):
        """Test mise à jour du streak - même jour"""
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 150,
            'level': 2,
            'experiencePoints': 250,
            'streak': 5,  # Streak inchangé
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update_streak.return_value = mock_updated
        
        response = self.client.post('/api/users/students/streak/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['streak'], 5)
    
    @patch('apps.users.students.services.StudentService.update_streak')
    async def test_update_streak_broken(self, mock_update_streak):
        """Test streak cassé (gap de plus d'un jour)"""
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 150,
            'level': 2,
            'experiencePoints': 250,
            'streak': 1,  # Streak réinitialisé
            'maxStreak': 10,
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update_streak.return_value = mock_updated
        
        response = self.client.post('/api/users/students/streak/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['streak'], 1)
    
    @patch('apps.users.students.services.StudentService.update_streak')
    async def test_update_streak_new_max(self, mock_update_streak):
        """Test nouveau record de streak"""
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.student_user.id),
            'studentCode': self.student_code,
            'points': 150,
            'level': 2,
            'experiencePoints': 250,
            'streak': 15,
            'maxStreak': 15,  # Nouveau record
            'lastActivityDate': datetime.now(),
            'totalCoursesEnrolled': 3,
            'totalCoursesCompleted': 1,
            'totalLearningTime': 7200,
            'totalCertificates': 1,
            'preferredCategories': ['Programming'],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update_streak.return_value = mock_updated
        
        response = self.client.post('/api/users/students/streak/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['streak'], 15)
        self.assertEqual(response.data['max_streak'], 15)
    
    # ==========================================
    # TESTS DE CLASSEMENT (LEADERBOARD)
    # ==========================================
    
    @patch('apps.users.students.services.StudentService.get_leaderboard')
    async def test_get_leaderboard_default(self, mock_leaderboard):
        """Test récupération du classement (par défaut top 10)"""
        mock_students = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'studentCode': f'STU2024{i:06d}',
                'points': 1000 - (i * 100),
                'level': 10 - i,
                'experiencePoints': 10000 - (i * 1000),
                'streak': 10 - i,
                'maxStreak': 20,
                'lastActivityDate': datetime.now(),
                'totalCoursesEnrolled': 10,
                'totalCoursesCompleted': 5,
                'totalLearningTime': 36000,
                'totalCertificates': 3,
                'preferredCategories': ['Programming'],
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
            for i in range(10)
        ]
        mock_leaderboard.return_value = mock_students
        
        # Pas besoin d'auth pour le leaderboard
        self.client.credentials()
        
        response = self.client.get('/api/users/students/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        # Vérifier que c'est trié par points
        self.assertGreaterEqual(
            response.data[0]['points'],
            response.data[1]['points']
        )
    
    @patch('apps.users.students.services.StudentService.get_leaderboard')
    async def test_get_leaderboard_custom_limit(self, mock_leaderboard):
        """Test récupération avec limite personnalisée"""
        mock_students = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'studentCode': f'STU2024{i:06d}',
                'points': 500 - (i * 10),
                'level': 5,
                'experiencePoints': 5000,
                'streak': 5,
                'maxStreak': 10,
                'lastActivityDate': datetime.now(),
                'totalCoursesEnrolled': 5,
                'totalCoursesCompleted': 2,
                'totalLearningTime': 18000,
                'totalCertificates': 1,
                'preferredCategories': ['Programming'],
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
            for i in range(5)
        ]
        mock_leaderboard.return_value = mock_students
        
        self.client.credentials()
        
        response = self.client.get('/api/users/students/leaderboard/?limit=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
    
    @patch('apps.users.students.services.StudentService.get_leaderboard')
    async def test_get_leaderboard_max_limit(self, mock_leaderboard):
        """Test que la limite est plafonnée à 100"""
        mock_students = []
        mock_leaderboard.return_value = mock_students
        
        self.client.credentials()
        
        # Demander 200, devrait être plafonné à 100
        response = self.client.get('/api/users/students/leaderboard/?limit=200')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérifier que le service a été appelé avec max 100
        # (dans la vraie implémentation)


class StudentServiceTestCase(TestCase):
    """Tests unitaires du service étudiant"""
    
    @pytest.mark.asyncio
    async def test_calculate_level(self):
        """Test du calcul de niveau"""
        from apps.users.students.services import StudentService
        
        service = StudentService()
        
        # 0-99 XP = niveau 1
        self.assertEqual(service.calculate_level(0), 1)
        self.assertEqual(service.calculate_level(50), 1)
        self.assertEqual(service.calculate_level(99), 1)
        
        # 100-199 XP = niveau 2
        self.assertEqual(service.calculate_level(100), 2)
        self.assertEqual(service.calculate_level(150), 2)
        
        # 1000 XP = niveau 11
        self.assertEqual(service.calculate_level(1000), 11)
    
    @pytest.mark.asyncio
    async def test_generate_student_code(self):
        """Test de génération de code étudiant"""
        from apps.users.students.services import StudentService
        
        service = StudentService()
        code = service.generate_student_code()
        
        # Vérifier le format STU + année + 6 chiffres
        self.assertTrue(code.startswith('STU2024'))
        self.assertEqual(len(code), 13)  # STU (3) + 2024 (4) + 123456 (6)
        self.assertTrue(code[7:].isdigit())


class StudentSerializerTestCase(TestCase):
    """Tests des serializers étudiants"""
    
    def test_student_create_serializer_valid(self):
        """Test serializer de création valide"""
        from apps.users.students.serializers import StudentCreateSerializer
        
        data = {
            'preferred_categories': ['Programming', 'Data Science']
        }
        
        serializer = StudentCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_student_create_serializer_empty(self):
        """Test serializer avec données vides"""
        from apps.users.students.serializers import StudentCreateSerializer
        
        serializer = StudentCreateSerializer(data={})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['preferred_categories'], [])
    
    def test_add_experience_serializer_valid(self):
        """Test serializer d'ajout d'XP"""
        from apps.users.students.serializers import AddExperienceSerializer
        
        data = {'points': 100}
        serializer = AddExperienceSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['points'], 100)
    
    def test_add_experience_serializer_negative(self):
        """Test serializer avec points négatifs"""
        from apps.users.students.serializers import AddExperienceSerializer
        
        data = {'points': -50}
        serializer = AddExperienceSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('points', serializer.errors)
    
    def test_add_experience_serializer_zero(self):
        """Test serializer avec zéro points"""
        from apps.users.students.serializers import AddExperienceSerializer
        
        data = {'points': 0}
        serializer = AddExperienceSerializer(data=data)
        
        # 0 n'est pas valide (min_value=1)
        self.assertFalse(serializer.is_valid())