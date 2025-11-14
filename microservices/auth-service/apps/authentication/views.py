from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from asgiref.sync import async_to_sync
import logging

from apps.authentication.services import (
    UserService,
    SessionService,
    MFAService,
    LoginHistoryService
)
from apps.authentication.serializers import *
from shared.shared.utils.ip_utils import get_client_ip, get_user_agent
from shared.shared.exceptions import *

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """Vue pour l'inscription"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
    
    def post(self, request):
        """Inscrire un nouvel utilisateur"""
        try:
            serializer = RegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer l'utilisateur
            user = async_to_sync(self.user_service.create_user)(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                role=serializer.validated_data.get('role', 'STUDENT')
            )
            
            # TODO: Envoyer un email de vérification
            
            response_serializer = UserSerializer(user)
            return Response({
                'user': response_serializer.data,
                'message': 'Registration successful. Please verify your email.'
            }, status=status.HTTP_201_CREATED)
            
        except UserAlreadyExistsError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )
        except WeakPasswordError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    """Vue pour la connexion"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
        self.session_service = SessionService()
        self.login_history_service = LoginHistoryService()
    
    def post(self, request):
        """Connecter un utilisateur"""
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Récupérer les informations de la requête
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            try:
                # Authentifier l'utilisateur
                user = async_to_sync(self.user_service.authenticate_user)(
                    email, password
                )
                
                # Vérifier si le MFA est activé
                if user.mfaEnabled:
                    # Logger la tentative
                    async_to_sync(self.login_history_service.log_login_attempt)(
                        user_id=user.id,
                        success=False,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        failure_reason='MFA required'
                    )
                    
                    return Response({
                        'requires_mfa': True,
                        'user_id': user.id,
                        'message': 'MFA code required'
                    }, status=status.HTTP_428_PRECONDITION_REQUIRED)
                
                # Créer une session
                session = async_to_sync(self.session_service.create_session)(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                # Créer un refresh token
                refresh_token = async_to_sync(self.session_service.create_refresh_token)(
                    user_id=user.id,
                    ip_address=ip_address
                )
                
                # Mettre à jour la dernière connexion
                async_to_sync(self.user_service.update_last_login)(
                    user.id, ip_address
                )
                
                # Logger la connexion réussie
                async_to_sync(self.login_history_service.log_login_attempt)(
                    user_id=user.id,
                    success=True,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                user_serializer = UserSerializer(user)
                
                return Response({
                    'user': user_serializer.data,
                    'access_token': session.token,
                    'refresh_token': refresh_token.token,
                    'expires_at': session.expiresAt.isoformat(),
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
                
            except InvalidCredentialsError:
                # Logger la tentative échouée
                user = async_to_sync(self.user_service.get_user_by_email)(email)
                if user:
                    async_to_sync(self.login_history_service.log_login_attempt)(
                        user_id=user.id,
                        success=False,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        failure_reason='Invalid credentials'
                    )
                
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except AccountLockedError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_423_LOCKED
                )
            except AccountSuspendedError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except EmailNotVerifiedError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MFALoginView(APIView):
    """Vue pour la connexion avec MFA"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
        self.session_service = SessionService()
        self.mfa_service = MFAService()
        self.login_history_service = LoginHistoryService()
    
    def post(self, request):
        """Connexion avec MFA"""
        try:
            serializer = MFALoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            mfa_code = serializer.validated_data['mfa_code']
            
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            # Authentifier l'utilisateur (sans vérifier l'email)
            user = async_to_sync(self.user_service.authenticate_user)(
                email, password, check_email_verified=False
            )
            
            # Vérifier le code MFA
            is_valid = async_to_sync(self.mfa_service.verify_mfa_code)(
                user.id, mfa_code
            )
            
            if not is_valid:
                # Logger l'échec
                async_to_sync(self.login_history_service.log_login_attempt)(
                    user_id=user.id,
                    success=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason='Invalid MFA code'
                )
                
                return Response(
                    {'error': 'Invalid MFA code'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Créer une session
            session = async_to_sync(self.session_service.create_session)(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            refresh_token = async_to_sync(self.session_service.create_refresh_token)(
                user_id=user.id,
                ip_address=ip_address
            )
            
            # Mettre à jour la dernière connexion
            async_to_sync(self.user_service.update_last_login)(user.id, ip_address)
            
            # Logger la connexion réussie
            async_to_sync(self.login_history_service.log_login_attempt)(
                user_id=user.id,
                success=True,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            user_serializer = UserSerializer(user)
            
            return Response({
                'user': user_serializer.data,
                'access_token': session.token,
                'refresh_token': refresh_token.token,
                'expires_at': session.expiresAt.isoformat(),
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"MFA login error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """Vue pour la déconnexion"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_service = SessionService()
    
    def post(self, request):
        """Déconnecter l'utilisateur"""
        try:
            # Récupérer le token de session depuis le header
            token = request.auth
            
            if token:
                # Invalider la session
                async_to_sync(self.session_service.invalidate_session)(str(token))
            
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    """Vue pour rafraîchir le token"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_service = SessionService()
    
    def post(self, request):
        """Rafraîchir le token de session"""
        try:
            serializer = RefreshTokenSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            refresh_token = serializer.validated_data['refresh_token']
            
            # Rafraîchir la session
            result = async_to_sync(self.session_service.refresh_session)(refresh_token)
            
            if not result:
                return Response(
                    {'error': 'Invalid or expired refresh token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Refresh token error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailView(APIView):
    """Vue pour vérifier l'email"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
    
    def post(self, request):
        """Vérifier l'email"""
        try:
            serializer = VerifyEmailSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            token = serializer.validated_data['token']
            
            success = async_to_sync(self.user_service.verify_email)(token)
            
            if not success:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'message': 'Email verified successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    class RequestPasswordResetView(APIView):
        """Vue pour demander une réinitialisation de mot de passe"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
    
    def post(self, request):
        """Demander un reset de mot de passe"""
        try:
            serializer = RequestPasswordResetSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            
            # Générer un token de reset
            token = async_to_sync(self.user_service.request_password_reset)(email)
            
            # TODO: Envoyer l'email avec le token
            
            # Toujours retourner succès pour ne pas révéler si l'email existe
            return Response(
                {'message': 'If the email exists, a reset link has been sent'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResetPasswordView(APIView):
    """Vue pour réinitialiser le mot de passe"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
    
    def post(self, request):
        """Réinitialiser le mot de passe"""
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            success = async_to_sync(self.user_service.reset_password)(
                token, new_password
            )
            
            if not success:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'message': 'Password reset successful'},
                status=status.HTTP_200_OK
            )
            
        except WeakPasswordError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangePasswordView(APIView):
    """Vue pour changer le mot de passe"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
    
    def post(self, request):
        """Changer le mot de passe"""
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = str(request.user.id)
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']
            
            success = async_to_sync(self.user_service.change_password)(
                user_id, current_password, new_password
            )
            
            if not success:
                return Response(
                    {'error': 'Failed to change password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
            
        except InvalidCredentialsError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except WeakPasswordError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MeView(APIView):
    """Vue pour récupérer les informations de l'utilisateur connecté"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()
    
    def get(self, request):
        """Récupérer les infos de l'utilisateur"""
        try:
            user_id = str(request.user.id)
            
            user = async_to_sync(self.user_service.get_user)(user_id)
            
            if not user:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get me error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============ MFA Views ============

class EnableMFAView(APIView):
    """Vue pour activer le MFA"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mfa_service = MFAService()
    
    def post(self, request):
        """Initier l'activation du MFA"""
        try:
            user_id = str(request.user.id)
            
            secret, totp_uri, backup_codes = async_to_sync(self.mfa_service.enable_mfa)(user_id)
            
            # Générer le QR code
            qr_code = self.mfa_service.generate_qr_code(totp_uri)
            
            return Response({
                'secret': secret,
                'qr_code': qr_code,
                'backup_codes': backup_codes,
                'message': 'Scan the QR code with your authenticator app and verify with a code'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Enable MFA error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyMFAView(APIView):
    """Vue pour vérifier et activer le MFA"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mfa_service = MFAService()
    
    def post(self, request):
        """Vérifier le code et activer le MFA"""
        try:
            serializer = VerifyMFASerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = str(request.user.id)
            code = serializer.validated_data['code']
            
            success = async_to_sync(self.mfa_service.verify_and_activate_mfa)(
                user_id, code
            )
            
            if not success:
                return Response(
                    {'error': 'Invalid verification code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'message': 'MFA activated successfully'},
                status=status.HTTP_200_OK
            )
            
        except InvalidMFACodeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Verify MFA error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DisableMFAView(APIView):
    """Vue pour désactiver le MFA"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mfa_service = MFAService()
    
    def post(self, request):
        """Désactiver le MFA"""
        try:
            serializer = DisableMFASerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = str(request.user.id)
            password = serializer.validated_data['password']
            
            success = async_to_sync(self.mfa_service.disable_mfa)(
                user_id, password
            )
            
            if not success:
                return Response(
                    {'error': 'Failed to disable MFA'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'message': 'MFA disabled successfully'},
                status=status.HTTP_200_OK
            )
            
        except InvalidMFACodeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Disable MFA error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegenerateBackupCodesView(APIView):
    """Vue pour régénérer les codes de backup"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mfa_service = MFAService()
    
    def post(self, request):
        """Régénérer les codes de backup"""
        try:
            user_id = str(request.user.id)
            
            backup_codes = async_to_sync(self.mfa_service.regenerate_backup_codes)(user_id)
            
            return Response({
                'backup_codes': backup_codes,
                'message': 'Backup codes regenerated successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Regenerate backup codes error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============ Session Management Views ============

class SessionsView(APIView):
    """Vue pour gérer les sessions"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_service = SessionService()
    
    def get(self, request):
        """Récupérer toutes les sessions actives"""
        try:
            user_id = str(request.user.id)
            
            sessions = async_to_sync(self.session_service.get_user_sessions)(user_id)
            
            serializer = SessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get sessions error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Révoquer toutes les sessions sauf la courante"""
        try:
            user_id = str(request.user.id)
            current_token = str(request.auth)
            
            count = async_to_sync(self.session_service.revoke_all_sessions)(
                user_id, except_token=current_token
            )
            
            return Response({
                'message': f'{count} sessions revoked successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Revoke sessions error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RevokeSessionView(APIView):
    """Vue pour révoquer une session spécifique"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_service = SessionService()
    
    def delete(self, request, session_id):
        """Révoquer une session"""
        try:
            # TODO: Vérifier que la session appartient à l'utilisateur
            
            success = async_to_sync(self.session_service.invalidate_session)(session_id)
            
            if not success:
                return Response(
                    {'error': 'Session not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': 'Session revoked successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Revoke session error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============ Login History Views ============

class LoginHistoryView(APIView):
    """Vue pour l'historique de connexion"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_history_service = LoginHistoryService()
    
    def get(self, request):
        """Récupérer l'historique de connexion"""
        try:
            user_id = str(request.user.id)
            limit = int(request.query_params.get('limit', 50))
            success_only = request.query_params.get('success_only', 'false').lower() == 'true'
            
            history = async_to_sync(self.login_history_service.get_user_login_history)(
                user_id, limit, success_only
            )
            
            serializer = LoginHistorySerializer(history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get login history error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginStatisticsView(APIView):
    """Vue pour les statistiques de connexion"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_history_service = LoginHistoryService()
    
    def get(self, request):
        """Récupérer les statistiques de connexion"""
        try:
            user_id = str(request.user.id)
            days = int(request.query_params.get('days', 30))
            
            stats = async_to_sync(self.login_history_service.get_login_statistics)(
                user_id, days
            )
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get login statistics error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
