from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import authenticate
import logging

from .models import CustomUser, OTPVerification, UserLoginHistory
from .serializers import (
    RegisterSerializer, LoginSerializer, OTPVerificationSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer,
    UserUpdateSerializer, LoginHistorySerializer, ChangePasswordSerializer
)
from .utils import generate_otp, send_otp_email, send_otp_sms

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication endpoints.
    Handles registration, login, OTP verification, and password management.
    """
    
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user.
        
        POST /api/register/
        {
            "phone": "+1234567890",
            "email": "user@example.com",
            "full_name": "John Doe",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and send OTP
            otp_code = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            
            OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=expires_at,
                purpose='registration'
            )
            
            # Simulate sending OTP (in production, use SMS gateway)
            logger.info(f"OTP for {user.phone}: {otp_code}")
            print(f"\n{'='*50}")
            print(f"OTP for registration: {otp_code}")
            print(f"Valid for 5 minutes")
            print(f"{'='*50}\n")
            
            return Response(
                {
                    "message": "Registration successful. Please verify your phone with OTP.",
                    "phone": user.phone,
                    "otp_sent_to": user.phone,
                    "user_id": str(user.id),
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_otp(self, request):
        """
        Verify OTP for registration or phone verification.
        
        POST /api/verify-otp/
        {
            "user_id": "uuid-here",
            "otp_code": "123456"
        }
        """
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp_code')
        
        if not user_id or not otp_code:
            return Response(
                {"error": "user_id and otp_code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            otp_obj = OTPVerification.objects.get(user=user, otp_code=otp_code)
        except OTPVerification.DoesNotExist:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return Response(
                {"error": "OTP has expired. Request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check max attempts
        if otp_obj.attempts >= otp_obj.max_attempts:
            return Response(
                {"error": "Maximum OTP verification attempts exceeded."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify OTP
        if otp_obj.otp_code == otp_code:
            otp_obj.is_verified = True
            otp_obj.verified_at = timezone.now()
            otp_obj.save()
            
            # Mark phone as verified
            user.is_phone_verified = True
            user.save()
            
            logger.info(f"Phone verified for user: {user.phone}")
            
            return Response(
                {
                    "message": "Phone verified successfully.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK
            )
        else:
            otp_obj.attempts += 1
            otp_obj.save()
            
            remaining_attempts = otp_obj.max_attempts - otp_obj.attempts
            return Response(
                {
                    "error": "Invalid OTP.",
                    "remaining_attempts": remaining_attempts,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        User login with phone/email and password.
        Returns JWT access and refresh tokens.
        
        POST /api/login/
        {
            "phone_or_email": "+1234567890",
            "password": "SecurePass123!"
        }
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # TODO: Implement OTP verification in production
            # For now, skip phone verification to allow testing
            # if not user.is_phone_verified:
            #     return Response(
            #         {
            #             "error": "Phone number not verified. Please verify with OTP first.",
            #             "user_id": str(user.id),
            #         },
            #         status=status.HTTP_403_FORBIDDEN
            #     )
            
            # Record login history
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            UserLoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Update last login
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"User logged in: {user.phone}")
            
            return Response(
                {
                    "message": "Login successful.",
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request):
        """
        Initiate forgot password flow - send OTP to user's phone.
        
        POST /api/forgot-password/
        {
            "phone_or_email": "+1234567890"
        }
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_or_email = serializer.validated_data['phone_or_email']
            
            # Get user
            try:
                user = CustomUser.objects.get(phone=phone_or_email)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.get(email=phone_or_email)
                except CustomUser.DoesNotExist:
                    # Security: don't reveal if user exists
                    return Response(
                        {"message": "If user exists, OTP will be sent."},
                        status=status.HTTP_200_OK
                    )
            
            # Generate OTP
            otp_code = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            
            # Delete previous OTP if exists
            OTPVerification.objects.filter(
                user=user,
                purpose='password_reset'
            ).delete()
            
            OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=expires_at,
                purpose='password_reset'
            )
            
            # Simulate sending OTP
            logger.info(f"Password reset OTP for {user.phone}: {otp_code}")
            print(f"\n{'='*50}")
            print(f"Password reset OTP: {otp_code}")
            print(f"Valid for 5 minutes")
            print(f"{'='*50}\n")
            
            return Response(
                {
                    "message": "OTP sent to your registered phone/email.",
                    "phone_or_email": phone_or_email,
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """
        Reset password using OTP verification.
        
        POST /api/reset-password/
        {
            "phone_or_email": "+1234567890",
            "otp_code": "123456",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_or_email = serializer.validated_data['phone_or_email']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            
            # Get user
            try:
                user = CustomUser.objects.get(phone=phone_or_email)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.get(email=phone_or_email)
                except CustomUser.DoesNotExist:
                    return Response(
                        {"error": "User not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Verify OTP
            try:
                otp_obj = OTPVerification.objects.get(
                    user=user,
                    otp_code=otp_code,
                    purpose='password_reset'
                )
            except OTPVerification.DoesNotExist:
                return Response(
                    {"error": "Invalid OTP."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if OTP is expired
            if otp_obj.is_expired():
                return Response(
                    {"error": "OTP has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as verified
            otp_obj.is_verified = True
            otp_obj.verified_at = timezone.now()
            otp_obj.save()
            
            logger.info(f"Password reset for user: {user.phone}")
            
            return Response(
                {
                    "message": "Password reset successfully.",
                    "phone_or_email": phone_or_email,
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout user (client should discard tokens).
        
        POST /api/logout/
        """
        logger.info(f"User logged out: {request.user.phone}")
        
        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Get current authenticated user's profile.
        
        GET /api/profile/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update user profile information.
        
        PATCH /api/update-profile/
        {
            "full_name": "New Name",
            "email": "newemail@example.com"
        }
        """
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated for user: {request.user.phone}")
            
            return Response(
                {
                    "message": "Profile updated successfully.",
                    "user": UserSerializer(request.user).data,
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change password for authenticated user.
        
        POST /api/change-password/
        {
            "old_password": "CurrentPass123!",
            "new_password": "NewSecurePass123!",
            "new_password_confirm": "NewSecurePass123!"
        }
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            logger.info(f"Password changed for user: {request.user.phone}")
            
            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def login_history(self, request):
        """
        Get user's login history.
        
        GET /api/login-history/
        """
        history = UserLoginHistory.objects.filter(user=request.user)[:10]
        serializer = LoginHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
