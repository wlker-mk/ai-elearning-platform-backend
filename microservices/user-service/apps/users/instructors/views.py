from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from asgiref.sync import async_to_sync
from .services import InstructorService
from .serializers import (
    InstructorSerializer,
    InstructorCreateSerializer,
    InstructorUpdateSerializer,
    InstructorPublicSerializer,
    RatingSerializer
)
import logging

logger = logging.getLogger(__name__)


class InstructorView(APIView):
    """Vue pour gérer le profil instructeur"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InstructorService()
    
    def get(self, request):
        """Récupérer le profil instructeur"""
        try:
            user_id = str(request.user.id)
            instructor = async_to_sync(self.service.get_instructor)(user_id)
            
            if not instructor:
                return Response(
                    {'error': 'Instructor profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = InstructorSerializer(instructor)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in InstructorView GET: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer un profil instructeur"""
        try:
            user_id = str(request.user.id)
            
            # Vérifier si existe déjà
            existing = async_to_sync(self.service.get_instructor)(user_id)
            if existing:
                return Response(
                    {'error': 'Instructor profile already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = InstructorCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            instructor = async_to_sync(self.service.create_instructor)(
                user_id,
                serializer.validated_data
            )
            
            response_serializer = InstructorSerializer(instructor)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in InstructorView POST: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Mettre à jour le profil instructeur"""
        try:
            user_id = str(request.user.id)
            
            serializer = InstructorUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            instructor = async_to_sync(self.service.update_instructor)(
                user_id,
                serializer.validated_data
            )
            
            if not instructor:
                return Response(
                    {'error': 'Instructor profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response_serializer = InstructorSerializer(instructor)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in InstructorView PUT: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorVerificationView(APIView):
    """Vue pour vérifier/déverifier un instructeur (Admin seulement)"""
    
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InstructorService()
    
    def post(self, request, user_id):
        """Vérifier un instructeur"""
        try:
            instructor = async_to_sync(self.service.verify_instructor)(user_id)
            
            if not instructor:
                return Response(
                    {'error': 'Instructor not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': 'Instructor verified successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error verifying instructor: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, user_id):
        """Retirer la vérification"""
        try:
            instructor = async_to_sync(self.service.unverify_instructor)(user_id)
            
            if not instructor:
                return Response(
                    {'error': 'Instructor not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': 'Instructor unverified successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error unverifying instructor: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicInstructorView(APIView):
    """Vue pour consulter le profil public d'un instructeur"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InstructorService()
    
    def get(self, request, user_id):
        """Récupérer le profil public"""
        try:
            instructor = async_to_sync(self.service.get_instructor)(user_id)
            
            if not instructor:
                return Response(
                    {'error': 'Instructor not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = InstructorPublicSerializer(instructor)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching public instructor: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TopInstructorsView(APIView):
    """Vue pour récupérer les meilleurs instructeurs"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InstructorService()
    
    def get(self, request):
        """Récupérer les meilleurs instructeurs"""
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(max(limit, 1), 50)
            
            instructors = async_to_sync(self.service.get_top_instructors)(limit)
            
            serializer = InstructorPublicSerializer(instructors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching top instructors: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorSearchView(APIView):
    """Vue pour rechercher des instructeurs"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InstructorService()
    
    def get(self, request):
        """Rechercher des instructeurs"""
        try:
            specialization = request.query_params.get('specialization')
            min_rating = request.query_params.get('min_rating')
            verified_only = request.query_params.get('verified_only', 'false').lower() == 'true'
            limit = int(request.query_params.get('limit', 20))
            
            if min_rating:
                min_rating = float(min_rating)
            
            instructors = async_to_sync(self.service.search_instructors)(
                specialization=specialization,
                min_rating=min_rating,
                verified_only=verified_only,
                limit=limit
            )
            
            serializer = InstructorPublicSerializer(instructors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error searching instructors: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )