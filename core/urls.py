from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RequestLoginCode, VerifyLoginCode,
    SpeciesViewSet, BreedViewSet, PetViewSet, PetVaccineViewSet, VaccineReminderViewSet,
    UserProfileView
)

router = DefaultRouter()
router.register(r'species', SpeciesViewSet)
router.register(r'breeds', BreedViewSet)
router.register(r'pets', PetViewSet)
router.register(r'vaccines', PetVaccineViewSet)
router.register(r'vaccine-reminders', VaccineReminderViewSet)

urlpatterns = [
    path('auth/request-code/', RequestLoginCode.as_view(), name='auth-request'),
    path('auth/verify-code/', VerifyLoginCode.as_view(), name='auth-verify'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('', include(router.urls)),
]