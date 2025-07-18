from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from .models import LoginCode, Species, Breed, Pet, UserProfile, Vaccine
from .serializers import SpeciesSerializer, BreedSerializer, PetSerializer, UserProfileSerializer, VaccineSerializer
from datetime import timedelta


class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class BreedViewSet(viewsets.ModelViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class VaccineViewSet(viewsets.ModelViewSet):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer


class RequestLoginCode(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a 6-digit code
        code = ''.join(random.choices(string.digits, k=6))

        # Save the code in the database
        LoginCode.objects.create(email=email, code=code)

        # Send the code by email
        try:
            send_mail(
                subject='Tu código de acceso a Petfans 🐾',
                message=f'Tu código es: {code}',
                from_email='hola@petfans.app',  # Use DEFAULT_FROM_EMAIL
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'error': 'No se pudo enviar el correo', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Código enviado al correo electrónico'}, status=status.HTTP_201_CREATED)


class VerifyLoginCode(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a valid code exists
        time_threshold = timezone.now() - timedelta(minutes=10)
        try:
            login_code = LoginCode.objects.get(
                email=email,
                code=code,
                used=False,
                created_at__gte=time_threshold
            )

            login_code.used = True
            login_code.save()

            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email}
            )

            refresh = RefreshToken.for_user(user)

            profile, _ = UserProfile.objects.get_or_create(user=user)

            # Verifica si falta completar nombre o teléfono
            profile_incomplete = not (profile.full_name and profile.phone_number)

            return Response({
                'message': 'Code verified successfully',
                'user_id': user.id,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'onboarding_required': profile_incomplete
            }, status=status.HTTP_200_OK)

        except LoginCode.DoesNotExist:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)