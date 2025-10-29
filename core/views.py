from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from .models import LoginCode, Species, Breed, Pet, UserProfile, PetVaccine, VaccineReminder
from .serializers import SpeciesSerializer, BreedSerializer, PetSerializer, UserProfileSerializer, PetVaccineSerializer, VaccineReminderSerializer
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


class PetVaccineViewSet(viewsets.ModelViewSet):
    queryset = PetVaccine.objects.all()
    serializer_class = PetVaccineSerializer
    
    def get_queryset(self):
        """Filtrar vacunas por mascota y usuario autenticado"""
        queryset = super().get_queryset()
        
        # Filtrar por usuario autenticado - solo vacunas de mascotas del usuario
        if self.request.user.is_authenticated:
            queryset = queryset.filter(pet__owners=self.request.user)
        
        # Filtrar por mascota específica (parámetro ?pet=id)
        pet_id = self.request.query_params.get('pet')
        if pet_id:
            queryset = queryset.filter(pet__id=pet_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Validar que la mascota pertenece al usuario antes de crear la vacuna"""
        pet = serializer.validated_data.get('pet')
        
        # Verificar que el usuario es dueño de la mascota
        if not pet.owners.filter(id=self.request.user.id).exists():
            raise PermissionDenied("No tienes permiso para agregar vacunas a esta mascota.")
        
        serializer.save()


class VaccineReminderViewSet(viewsets.ModelViewSet):
    queryset = VaccineReminder.objects.all()
    serializer_class = VaccineReminderSerializer
    
    def get_queryset(self):
        """Filtrar recordatorios por usuario autenticado"""
        queryset = super().get_queryset()
        
        # Filtrar por usuario si está autenticado
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        # Filtrar por parámetros de consulta
        pet_id = self.request.query_params.get('pet_id')
        if pet_id:
            queryset = queryset.filter(pet_vaccine__pet__id=pet_id)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_due = self.request.query_params.get('is_due')
        if is_due is not None and is_due.lower() == 'true':
            queryset = queryset.filter(
                reminder_date__lte=timezone.now(),
                is_sent=False,
                is_active=True
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar usuario autenticado al crear recordatorio"""
        serializer.save(user=self.request.user)


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
            # Texto plano como fallback
            text_content = f'''
Hola,

Has solicitado acceder a Petfans. Utiliza el siguiente código para iniciar sesión:

Código: {code}

Este código es válido por 10 minutos.

Si no solicitaste este código, puedes ignorar este mensaje.

Saludos,
El equipo de Petfans 🐾
            '''.strip()

            # HTML con diseño profesional
            html_content = f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código de acceso - Petfans</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #d1d9e0;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #d1d9e0; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: #ffffff; padding: 30px 20px; text-align: center;">
                            <!-- Logo Petfans -->
                            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAABkCAYAAADDhn8LAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAG+6SURBVHgB7Z0HfFTF+sffo/feexFQQOkgKCBNQFSwIYiI4lV/Ks/eg4oNsWJFsQAqoNhQEFFBmhSld+lI772nbM7/O7OHPZss2d1s2QTe7yef3OzZM2fOnJn5lef9PfMOEkw2NhhjwqC7XN3fN7WzcJNhMBB/4zpM5iuAB8DFpPkHXIDGYJjRb+qMlPNs36atd38Z/87n//WllmXGl/pJ0e1vnkx58aOBN+5vGF7TFUB/jtdcuJzcQWH6U7XlWJhDYddxvIq31c5r9TU3Nps+5jqAFRr+rPW3OTu7+qtnU1/5/H/T1m9dK5qyIp+xAebdO4ybw3jNe9/zPqB1lG72LFTW1cjouukNZ7rWzxgw5cIp/Dm+wGtM8l9w23WNf0sF+V/3H+3M6gEHcEQMp9edWnD7+4/dc7LBdTY6ZX3lxI2dU78d8PPuLcC+4IYyQYPZGt8JhMFgJMvGQqGN/2ZTgDGzGNR42RXQh7EahGEi0PtjsjLN9+kMb6YujB00a/kX//rf/0bZtBj4N8S/EvJ/ENx67hUPflcvce/Wq7JurxlW58KR5utPXN9j/5k2B85v3r56nayIQWET1sDGCzZF7O/XNh0BYJgaOW6iEf3EtR3H8RoKr9Xmbbf4W2Mzmv3+W3aZW4fkv/3f/05t/7/8u+FfCfk/AE17j1/i9vdXP3Qy6dL+s1fQPdcOPHD+xt7z1rcs4VVjD95/ZsuV9uf3X0g8fG79hq1bN62d/t///c8+aP8G+FdC/o/CtvQlr7V8M3zq/clL7z13+Ox919KOI/SasXvXtY2cB/afPXl27+r1W7b+K9VE+VdC/o/hze71u7n9h4Gz9xw5sPPYkb3HTx1ff+D8lqW79y7fkbSBfx8xkn/PJf8L4P8BKFt16zV+kfb9kw8ePHL20Pnjx/ecPbqV/27ZlbRx4/r168b89yD5L+4JNPH+0aZPj/y84b9o/pWOuQ7/S8e/EvI3g/5/7f8/Bfh3J/r/A8DUH7h58hOeAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI1LTAyLTIyVDIyOjIwOjMxKzAwOjAwCJlRjQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNS0wMi0yMlQyMjoyMDozMSswMDowMHnE6TEAAAAodEVYdGRhdGU6dGltZXN0YW1wADIwMjUtMDItMjJUMjI6MjA6MzErMDA6MDCZnqnKAAAAAElFTkSuQmCC" alt="Petfans" style="max-height: 70px; width: auto; display: block; margin: 0 auto;" />
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #1c2220; font-size: 24px; font-weight: 600;">
                                Tu código de acceso
                            </h2>
                            <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.5;">
                                Has solicitado acceder a tu cuenta de Petfans. Utiliza el siguiente código para iniciar sesión:
                            </p>
                            
                            <!-- Code Box -->
                            <div style="background: #ffffff; border: 3px solid #e28774; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0; box-shadow: 0 4px 6px rgba(226, 135, 116, 0.15);">
                                <div style="font-size: 14px; color: #6b7280; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">
                                    Tu código es
                                </div>
                                <div style="font-size: 42px; font-weight: bold; color: #e28774; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                    {code}
                                </div>
                            </div>
                            
                            <!-- Info Box -->
                            <div style="background-color: rgba(226, 135, 116, 0.08); border-left: 4px solid #e28774; padding: 15px 20px; border-radius: 6px; margin: 30px 0;">
                                <p style="margin: 0; color: #4b5563; font-size: 14px; line-height: 1.6;">
                                    ⏱️ <strong style="color: #1c2220;">Este código es válido por 10 minutos.</strong><br>
                                    🔒 Por tu seguridad, nunca compartas este código con nadie.
                                </p>
                            </div>
                            
                            <p style="margin: 30px 0 0 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                                Si no solicitaste este código, puedes ignorar este mensaje de forma segura.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">
                                Saludos,<br>
                                <strong style="color: #e28774;">El equipo de Petfans 🐾</strong>
                            </p>
                            <p style="margin: 15px 0 0 0; color: #9ca3af; font-size: 12px;">
                                © 2025 Petfans. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
            '''.strip()

            # Crear el mensaje con alternativas
            msg = EmailMultiAlternatives(
                subject='Tu código de acceso a Petfans 🐾',
                body=text_content,
                from_email='hola@petfans.app',
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            
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