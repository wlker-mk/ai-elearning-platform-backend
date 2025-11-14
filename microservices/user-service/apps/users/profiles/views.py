from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from .services import ProfileService
from .serializers import ProfileSerializer, ProfileCreateSerializer, ProfileUpdateSerializer
import logging

logger = logging.getLogger(__name__)


class ProfileView(APIView):
    """Vue pour gérer les profils utilisateurs"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProfileService()
    
    def get(self, request):
        """Récupérer le profil de l'utilisateur connecté"""
        try:
            user_id = str(request.user.id)
            profile = async_to_sync(self.service.get_profile)(user_id)
            
            if not profile:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ProfileView GET: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Créer un profil pour l'utilisateur connecté"""
        try:
            user_id = str(request.user.id)
            
            # Vérifier si le profil existe déjà
            existing_profile = async_to_sync(self.service.get_profile)(user_id)
            if existing_profile:
                return Response(
                    {'error': 'Profile already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ProfileCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            profile = async_to_sync(self.service.create_profile)(
                user_id,
                serializer.validated_data
            )
            
            response_serializer = ProfileSerializer(profile)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error in ProfileView POST: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Mettre à jour le profil de l'utilisateur connecté"""
        try:
            user_id = str(request.user.id)
            
            serializer = ProfileUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            profile = async_to_sync(self.service.update_profile)(
                user_id,
                serializer.validated_data
            )
            
            if not profile:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response_serializer = ProfileSerializer(profile)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ProfileView PUT: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Supprimer le profil de l'utilisateur connecté"""
        try:
            user_id = str(request.user.id)
            
            success = async_to_sync(self.service.delete_profile)(user_id)
            
            if success:
                return Response(
                    {'message': 'Profile deleted successfully'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as e:
            logger.error(f"Error in ProfileView DELETE: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicProfileView(APIView):
    """Vue pour consulter les profils publics"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProfileService()
    
    def get(self, request, user_id):
        """Récupérer le profil public d'un utilisateur"""
        try:
            profile = async_to_sync(self.service.get_profile)(user_id)
            
            if not profile:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PublicProfileView GET: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
