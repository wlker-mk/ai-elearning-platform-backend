from django.urls import path
from apps.authentication.views import (
    # Auth
    HealthCheckView,
    RegisterView,
    LoginView,
    MFALoginView,
    LogoutView,
    RefreshTokenView,
    VerifyEmailView,
    RequestPasswordResetView,
    ResetPasswordView,
    ChangePasswordView,
    MeView,
    # MFA
    EnableMFAView,
    VerifyMFAView,
    DisableMFAView,
    RegenerateBackupCodesView,
    # Sessions
    SessionsView,
    RevokeSessionView,
    # Login History
    LoginHistoryView,
    LoginStatisticsView,
    
    # OAuth
    GoogleOAuthView,
    GitHubOAuthView,
    LinkOAuthView,
    UnlinkOAuthView,
)

app_name = 'authentication'

urlpatterns = [
    
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/mfa/', MFALoginView.as_view(), name='mfa-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('password/request-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password/reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('password/change/', ChangePasswordView.as_view(), name='change-password'),
    path('me/', MeView.as_view(), name='me'),
    path('health/', HealthCheckView.as_view(), name='health'),
    
    # MFA
    path('mfa/enable/', EnableMFAView.as_view(), name='enable-mfa'),
    path('mfa/verify/', VerifyMFAView.as_view(), name='verify-mfa'),
    path('mfa/disable/', DisableMFAView.as_view(), name='disable-mfa'),
    path('mfa/backup-codes/', RegenerateBackupCodesView.as_view(), name='regenerate-backup-codes'),
    
    # Sessions
    path('sessions/', SessionsView.as_view(), name='sessions'),
    path('sessions/<str:session_id>/', RevokeSessionView.as_view(), name='revoke-session'),
    
    # Login History
    path('login-history/', LoginHistoryView.as_view(), name='login-history'),
    path('login-statistics/', LoginStatisticsView.as_view(), name='login-statistics'),
    
    # OAuth
    path('oauth/google/', GoogleOAuthView.as_view(), name='google-oauth'),
    path('oauth/github/', GitHubOAuthView.as_view(), name='github-oauth'),
    path('oauth/link/', LinkOAuthView.as_view(), name='link-oauth'),
    path('oauth/unlink/', UnlinkOAuthView.as_view(), name='unlink-oauth'),
]