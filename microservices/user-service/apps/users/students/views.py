from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from .services import StudentService
from .serializers import (
    StudentSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
    AddExperienceSerializer
)
import logging

logger = logging.getLogger(__name__)


class StudentView(APIView):
    """Vue pour gérer le profil étudiant"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StudentService()
    
    def get(self, request):
        """Récupérer le profil étudiant"""
        try:
            user_id = str(request.user.id)
            student = async_to_sync(self.service.get_student)(user_id)
            
            if not student:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in StudentView GET: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer un profil étudiant"""
        try:
            user_id = str(request.user.id)
            
            # Vérifier si existe déjà
            existing = async_to_sync(self.service.get_student)(user_id)
            if existing:
                return Response(
                    {'error': 'Student profile already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = StudentCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            student = async_to_sync(self.service.create_student)(
                user_id,
                serializer.validated_data
            )
            
            response_serializer = StudentSerializer(student)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in StudentView POST: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Mettre à jour le profil étudiant"""
        try:
            user_id = str(request.user.id)
            
            serializer = StudentUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            student = async_to_sync(self.service.update_student)(
                user_id,
                serializer.validated_data
            )
            
            if not student:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response_serializer = StudentSerializer(student)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in StudentView PUT: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentExperienceView(APIView):
    """Vue pour gérer l'expérience de l'étudiant"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StudentService()
    
    def post(self, request):
        """Ajouter de l'expérience"""
        try:
            user_id = str(request.user.id)
            
            serializer = AddExperienceSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            student = async_to_sync(self.service.add_experience_points)(
                user_id,
                serializer.validated_data['points']
            )
            
            if not student:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response_serializer = StudentSerializer(student)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error adding experience: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentStreakView(APIView):
    """Vue pour gérer le streak"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StudentService()
    
    def post(self, request):
        """Mettre à jour le streak"""
        try:
            user_id = str(request.user.id)
            
            student = async_to_sync(self.service.update_streak)(user_id)
            
            if not student:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating streak: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeaderboardView(APIView):
    """Vue pour le classement"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StudentService()
    
    def get(self, request):
        """Récupérer le classement"""
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(max(limit, 1), 100)  # Entre 1 et 100
            
            students = async_to_sync(self.service.get_leaderboard)(limit)
            
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
