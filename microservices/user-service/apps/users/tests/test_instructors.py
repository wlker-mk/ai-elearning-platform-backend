# apps/users/tests/test_instructors.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from datetime import datetime
from unittest.mock import patch

User = get_user_model()


class InstructorAPITestCase(APITestCase):
    """Tests pour les endpoints instructeurs"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = APIClient()
        
        # Créer un instructeur
        self.instructor_user = User.objects.create_user(
            id=uuid.uuid4(),
            email='instructor@test.com',
            username='instructor',
            password='InstructorPass123!',
            role='instructor'
        )
        
        # Créer un admin
        self.admin_user = User.objects.create_user(
            id=uuid.uuid4(),
            email='admin@test.com',
            username='admin',
            password='AdminPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Token instructeur
        refresh = RefreshToken.for_user(self.instructor_user)
        self.instructor_token = str(refresh.access_token)
        
        # Token admin
        refresh_admin = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(refresh_admin.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        
        self.instructor_code = 'INS2024123456'
    
    def tearDown(self):
        """Nettoyage"""
        User.objects.all().delete()
    
    # ==========================================
    # TESTS DE CRÉATION DE PROFIL INSTRUCTEUR
    # ==========================================
    
    @patch('apps.users.instructors.services.InstructorService.create_instructor')
    async def test_create_instructor_success(self, mock_create):
        """Test création profil instructeur avec succès"""
        mock_instructor = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'title': 'Senior Developer',
            'headline': 'Expert in Python and Django',
            'specializations': ['Python', 'Django', 'REST API'],
            'expertise': ['Backend Development', 'Database Design'],
            'certifications': ['AWS Certified', 'Python Expert'],
            'yearsOfExperience': 5,
            'hourlyRate': 50.00,
            'rating': 0.0,
            'totalReviews': 0,
            'totalStudents': 0,
            'totalCourses': 0,
            'isVerified': False,
            'verifiedAt': None,
            'bankAccount': None,
            'bankName': None,
            'paypalEmail': None,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_create.return_value = mock_instructor
        
        data = {
            'title': 'Senior Developer',
            'headline': 'Expert in Python and Django',
            'specializations': ['Python', 'Django', 'REST API'],
            'expertise': ['Backend Development', 'Database Design'],
            'certifications': ['AWS Certified', 'Python Expert'],
            'years_of_experience': 5,
            'hourly_rate': 50.00
        }
        
        response = self.client.post(
            '/api/users/instructors/me/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('instructor_code', response.data)
        self.assertEqual(response.data['title'], 'Senior Developer')
        self.assertEqual(response.data['years_of_experience'], 5)
    
    @patch('apps.users.instructors.services.InstructorService.get_instructor')
    async def test_create_instructor_already_exists(self, mock_get):
        """Test création quand le profil existe déjà"""
        mock_get.return_value = {'userId': str(self.instructor_user.id)}
        
        data = {
            'title': 'Developer',
            'specializations': ['Python']
        }
        
        response = self.client.post(
            '/api/users/instructors/me/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', response.data['error'].lower())
    
    @patch('apps.users.instructors.services.InstructorService.create_instructor')
    async def test_create_instructor_minimal_data(self, mock_create):
        """Test création avec données minimales"""
        mock_instructor = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'title': None,
            'headline': None,
            'specializations': [],
            'expertise': [],
            'certifications': [],
            'yearsOfExperience': 0,
            'hourlyRate': None,
            'rating': 0.0,
            'totalReviews': 0,
            'totalStudents': 0,
            'totalCourses': 0,
            'isVerified': False,
            'verifiedAt': None,
            'bankAccount': None,
            'bankName': None,
            'paypalEmail': None,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_create.return_value = mock_instructor
        
        response = self.client.post('/api/users/instructors/me/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_instructor_negative_experience(self):
        """Test création avec expérience négative"""
        data = {
            'years_of_experience': -5
        }
        
        response = self.client.post(
            '/api/users/instructors/me/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('years_of_experience', response.data)
    
    def test_create_instructor_negative_rate(self):
        """Test création avec taux horaire négatif"""
        data = {
            'hourly_rate': -50.00
        }
        
        response = self.client.post(
            '/api/users/instructors/me/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('hourly_rate', response.data)
    
    # ==========================================
    # TESTS DE RÉCUPÉRATION DE PROFIL
    # ==========================================
    
    @patch('apps.users.instructors.services.InstructorService.get_instructor')
    async def test_get_instructor_success(self, mock_get):
        """Test récupération profil instructeur"""
        mock_instructor = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'title': 'Senior Developer',
            'headline': 'Expert in Python and Django',
            'specializations': ['Python', 'Django'],
            'expertise': ['Backend Development'],
            'certifications': ['AWS Certified'],
            'yearsOfExperience': 5,
            'hourlyRate': 50.00,
            'rating': 4.5,
            'totalReviews': 10,
            'totalStudents': 100,
            'totalCourses': 5,
            'isVerified': True,
            'verifiedAt': datetime.now(),
            'bankAccount': 'XXXX1234',
            'bankName': 'Test Bank',
            'paypalEmail': 'instructor@paypal.com',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_get.return_value = mock_instructor
        
        response = self.client.get('/api/users/instructors/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Senior Developer')
        self.assertEqual(response.data['rating'], 4.5)
        self.assertEqual(response.data['total_students'], 100)
    
    @patch('apps.users.instructors.services.InstructorService.get_instructor')
    async def test_get_instructor_not_found(self, mock_get):
        """Test récupération profil inexistant"""
        mock_get.return_value = None
        
        response = self.client.get('/api/users/instructors/me/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('apps.users.instructors.services.InstructorService.get_instructor')
    async def test_get_public_instructor_profile(self, mock_get):
        """Test récupération d'un profil public"""
        other_instructor_id = str(uuid.uuid4())
        mock_instructor = {
            'id': str(uuid.uuid4()),
            'userId': other_instructor_id,
            'instructorCode': 'INS2024999999',
            'title': 'Data Scientist',
            'headline': 'ML Expert',
            'specializations': ['Machine Learning', 'Python'],
            'expertise': ['Data Science'],
            'certifications': ['TensorFlow Certified'],
            'yearsOfExperience': 8,
            'hourlyRate': 75.00,
            'rating': 4.8,
            'totalReviews': 50,
            'totalStudents': 500,
            'totalCourses': 10,
            'isVerified': True,
            'verifiedAt': datetime.now(),
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_get.return_value = mock_instructor
        
        # Pas besoin d'auth pour profil public
        self.client.credentials()
        
        response = self.client.get(f'/api/users/instructors/{other_instructor_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Data Scientist')
        # Vérifier que les infos bancaires ne sont pas exposées
        self.assertNotIn('bank_account', response.data)
        self.assertNotIn('paypal_email', response.data)
    
    # ==========================================
    # TESTS DE MISE À JOUR
    # ==========================================
    
    @patch('apps.users.instructors.services.InstructorService.update_instructor')
    async def test_update_instructor_success(self, mock_update):
        """Test mise à jour profil instructeur"""
        update_data = {
            'title': 'Lead Developer',
            'hourly_rate': 60.00,
            'specializations': ['Python', 'Django', 'FastAPI']
        }
        
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'title': 'Lead Developer',
            'headline': 'Expert in Python and Django',
            'specializations': ['Python', 'Django', 'FastAPI'],
            'expertise': ['Backend Development'],
            'certifications': ['AWS Certified'],
            'yearsOfExperience': 5,
            'hourlyRate': 60.00,
            'rating': 4.5,
            'totalReviews': 10,
            'totalStudents': 100,
            'totalCourses': 5,
            'isVerified': True,
            'verifiedAt': datetime.now(),
            'bankAccount': 'XXXX1234',
            'bankName': 'Test Bank',
            'paypalEmail': 'instructor@paypal.com',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update.return_value = mock_updated
        
        response = self.client.put(
            '/api/users/instructors/me/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Lead Developer')
        self.assertEqual(response.data['hourly_rate'], 60.00)
    
    @patch('apps.users.instructors.services.InstructorService.update_instructor')
    async def test_update_instructor_partial(self, mock_update):
        """Test mise à jour partielle"""
        update_data = {'headline': 'Updated headline'}
        
        mock_updated = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'title': 'Senior Developer',
            'headline': 'Updated headline',
            'specializations': ['Python'],
            'expertise': ['Backend Development'],
            'certifications': [],
            'yearsOfExperience': 5,
            'hourlyRate': 50.00,
            'rating': 4.5,
            'totalReviews': 10,
            'totalStudents': 100,
            'totalCourses': 5,
            'isVerified': False,
            'verifiedAt': None,
            'bankAccount': None,
            'bankName': None,
            'paypalEmail': None,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_update.return_value = mock_updated
        
        response = self.client.put(
            '/api/users/instructors/me/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['headline'], 'Updated headline')
    
    # ==========================================
    # TESTS DE VÉRIFICATION (ADMIN ONLY)
    # ==========================================
    
    @patch('apps.users.instructors.services.InstructorService.verify_instructor')
    async def test_verify_instructor_as_admin(self, mock_verify):
        """Test vérification par un admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        mock_verified = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'title': 'Senior Developer',
            'headline': 'Expert',
            'specializations': ['Python'],
            'expertise': ['Backend'],
            'certifications': [],
            'yearsOfExperience': 5,
            'hourlyRate': 50.00,
            'rating': 4.5,
            'totalReviews': 10,
            'totalStudents': 100,
            'totalCourses': 5,
            'isVerified': True,
            'verifiedAt': datetime.now(),
            'bankAccount': None,
            'bankName': None,
            'paypalEmail': None,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
        }
        mock_verify.return_value = mock_verified
        
        response = self.client.post(
            f'/api/users/instructors/verify/{self.instructor_user.id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('verified', response.data['message'].lower())
    
    def test_verify_instructor_as_non_admin(self):
        """Test vérification par un non-admin (devrait échouer)"""
        # Utiliser le token instructeur (non admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
        
        response = self.client.post(
            f'/api/users/instructors/verify/{self.instructor_user.id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('apps.users.instructors.services.InstructorService.unverify_instructor')
    async def test_unverify_instructor_as_admin(self, mock_unverify):
        """Test retrait de vérification par un admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        mock_unverified = {
            'id': str(uuid.uuid4()),
            'userId': str(self.instructor_user.id),
            'instructorCode': self.instructor_code,
            'isVerified': False,
            'verifiedAt': None,
        }
        mock_unverify.return_value = mock_unverified
        
        response = self.client.delete(
            f'/api/users/instructors/verify/{self.instructor_user.id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unverified', response.data['message'].lower())
    
    # ==========================================
    # TESTS DES MEILLEURS INSTRUCTEURS
    # ==========================================
    
    @patch('apps.users.instructors.services.InstructorService.get_top_instructors')
    async def test_get_top_instructors_default(self, mock_top):
        """Test récupération des meilleurs instructeurs"""
        mock_instructors = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'instructorCode': f'INS2024{i:06d}',
                'title': f'Instructor {i}',
                'headline': 'Expert',
                'specializations': ['Python'],
                'expertise': ['Backend'],
                'certifications': [],
                'yearsOfExperience': 10 - i,
                'hourlyRate': 50.00,
                'rating': 5.0 - (i * 0.1),
                'totalReviews': 100 - (i * 10),
                'totalStudents': 1000 - (i * 100),
                'totalCourses': 10 - i,
                'isVerified': True,
                'verifiedAt': datetime.now(),
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
            for i in range(10)
        ]
        mock_top.return_value = mock_instructors
        
        self.client.credentials()  # Pas besoin d'auth
        
        response = self.client.get('/api/users/instructors/top/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        # Vérifier tri par rating
        self.assertGreaterEqual(
            response.data[0]['rating'],
            response.data[1]['rating']
        )
    
    @patch('apps.users.instructors.services.InstructorService.get_top_instructors')
    async def test_get_top_instructors_custom_limit(self, mock_top):
        """Test avec limite personnalisée"""
        mock_instructors = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'instructorCode': f'INS2024{i:06d}',
                'title': 'Instructor',
                'headline': 'Expert',
                'specializations': ['Python'],
                'expertise': ['Backend'],
                'certifications': [],
                'yearsOfExperience': 5,
                'hourlyRate': 50.00,
                'rating': 4.5,
                'totalReviews': 50,
                'totalStudents': 200,
                'totalCourses': 5,
                'isVerified': True,
                'verifiedAt': datetime.now(),
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
            for i in range(5)
        ]
        mock_top.return_value = mock_instructors
        
        self.client.credentials()
        
        response = self.client.get('/api/users/instructors/top/?limit=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
    
    # ==========================================
    # TESTS DE RECHERCHE D'INSTRUCTEURS
    # ==========================================
    
    @patch('apps.users.instructors.services.InstructorService.search_instructors')
    async def test_search_by_specialization(self, mock_search):
        """Test recherche par spécialisation"""
        mock_results = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'instructorCode': 'INS2024111111',
                'title': 'Python Expert',
                'headline': 'Python specialist',
                'specializations': ['Python', 'Django'],
                'expertise': ['Backend'],
                'certifications': [],
                'yearsOfExperience': 5,
                'hourlyRate': 50.00,
                'rating': 4.5,
                'totalReviews': 20,
                'totalStudents': 150,
                'totalCourses': 5,
                'isVerified': True,
                'verifiedAt': datetime.now(),
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
        ]
        mock_search.return_value = mock_results
        
        self.client.credentials()
        
        response = self.client.get('/api/users/instructors/search/?specialization=Python')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertIn('Python', response.data[0]['specializations'])
    
    @patch('apps.users.instructors.services.InstructorService.search_instructors')
    async def test_search_by_min_rating(self, mock_search):
        """Test recherche par note minimale"""
        mock_results = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'instructorCode': 'INS2024222222',
                'title': 'Excellent Instructor',
                'headline': 'Top rated',
                'specializations': ['Python'],
                'expertise': ['Backend'],
                'certifications': [],
                'yearsOfExperience': 8,
                'hourlyRate': 75.00,
                'rating': 4.8,
                'totalReviews': 100,
                'totalStudents': 500,
                'totalCourses': 10,
                'isVerified': True,
                'verifiedAt': datetime.now(),
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
        ]
        mock_search.return_value = mock_results
        
        self.client.credentials()
        
        response = self.client.get('/api/users/instructors/search/?min_rating=4.5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for instructor in response.data:
            self.assertGreaterEqual(instructor['rating'], 4.5)
    
    @patch('apps.users.instructors.services.InstructorService.search_instructors')
    async def test_search_verified_only(self, mock_search):
        """Test recherche instructeurs vérifiés uniquement"""
        mock_results = [
            {
                'id': str(uuid.uuid4()),
                'userId': str(uuid.uuid4()),
                'instructorCode': 'INS2024333333',
                'title': 'Verified Instructor',
                'headline': 'Trusted',
                'specializations': ['Python'],
                'expertise': ['Backend'],
                'certifications': [],
                'yearsOfExperience': 5,
                'hourlyRate': 50.00,
                'rating': 4.5,
                'totalReviews': 50,
                'totalStudents': 200,
                'totalCourses': 5,
                'isVerified': True,
                'verifiedAt': datetime.now(),
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
        ]
        mock_search.return_value = mock_results
        
        self.client.credentials()
        
        response = self.client.get('/api/users/instructors/search/?verified_only=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for instructor in response.data:
            self.assertTrue(instructor['is_verified'])
    
    @patch('apps.users.instructors.services.InstructorService.search_instructors')
    async def test_search_combined_filters(self, mock_search):
        """Test recherche avec plusieurs filtres"""
        mock_results = []
        mock_search.return_value = mock_results
        
        self.client.credentials()
        
        response = self.client.get(
            '/api/users/instructors/search/'
            '?specialization=Python&min_rating=4.0&verified_only=true&limit=5'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InstructorServiceTestCase(TestCase):
    """Tests unitaires du service instructeur"""
    
    @pytest.mark.asyncio
    async def test_generate_instructor_code(self):
        """Test génération de code instructeur"""
        from apps.users.instructors.services import InstructorService
        
        service = InstructorService()
        code = service.generate_instructor_code()
        
        # Format: INS + année + 6 chiffres
        self.assertTrue(code.startswith('INS2024'))
        self.assertEqual(len(code), 13)
        self.assertTrue(code[7:].isdigit())