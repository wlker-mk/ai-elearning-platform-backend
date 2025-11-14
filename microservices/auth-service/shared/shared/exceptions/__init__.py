from rest_framework.exceptions import APIException
from rest_framework import status


class AuthenticationError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed.'
    default_code = 'authentication_failed'


class InvalidCredentialsError(AuthenticationError):
    default_detail = 'Invalid email or password.'
    default_code = 'invalid_credentials'


class AccountLockedError(AuthenticationError):
    status_code = status.HTTP_423_LOCKED
    default_detail = 'Account is temporarily locked due to multiple failed login attempts.'
    default_code = 'account_locked'


class AccountSuspendedError(AuthenticationError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Account has been suspended.'
    default_code = 'account_suspended'


class EmailNotVerifiedError(AuthenticationError):
    default_detail = 'Email address is not verified.'
    default_code = 'email_not_verified'


class MFARequiredError(APIException):
    status_code = status.HTTP_428_PRECONDITION_REQUIRED
    default_detail = 'Multi-factor authentication is required.'
    default_code = 'mfa_required'


class InvalidMFACodeError(AuthenticationError):
    default_detail = 'Invalid MFA code.'
    default_code = 'invalid_mfa_code'


class TokenExpiredError(AuthenticationError):
    default_detail = 'Token has expired.'
    default_code = 'token_expired'


class InvalidTokenError(AuthenticationError):
    default_detail = 'Invalid token.'
    default_code = 'invalid_token'


class UserAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'User with this email already exists.'
    default_code = 'user_exists'


class WeakPasswordError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Password does not meet security requirements.'
    default_code = 'weak_password'