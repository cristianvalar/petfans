from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


class Species(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Species"
        verbose_name_plural = "Species"

    def __str__(self):
        return self.name


class Breed(models.Model):
    name = models.CharField(max_length=255)
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='breeds')

    class Meta:
        verbose_name = "Breed"
        verbose_name_plural = "Breeds"
        unique_together = ['name', 'species']

    def __str__(self):
        return f"{self.name} ({self.species.name})"


class Pet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    species = models.ForeignKey(Species, on_delete=models.PROTECT, related_name='pets')
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT, related_name='pets', blank=True, null=True)
    sex = models.CharField(max_length=50, blank=True, null=True, verbose_name='Sexo')
    birth_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    photo = models.ImageField(upload_to='pets/', blank=True, null=True)
    chip_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número de chip')
    is_sterilized = models.BooleanField(null=True, blank=True, verbose_name='Esterilizado/a')
    owners = models.ManyToManyField(User, related_name='pets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

    def __str__(self):
        owners_str = ", ".join([owner.username for owner in self.owners.all()[:3]])
        if self.owners.count() > 3:
            owners_str += "..."
        breed_str = f" - {self.breed.name}" if self.breed else ""
        return f"{self.name} - {self.species.name}{breed_str} ({owners_str})"

    @property
    def current_age(self):
        if self.birth_date:
            return (timezone.now().date() - self.birth_date).days // 365
        return None
    


class Vaccine(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='vaccines')
    name = models.CharField(max_length=255)
    applied_date = models.DateField()
    next_dose = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vaccine"
        verbose_name_plural = "Vaccines"

    def __str__(self):
        return f"{self.name} - {self.pet.name} ({self.applied_date})"


class LoginCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Login Code"
        verbose_name_plural = "Login Codes"

    def is_valid(self):
        return not self.used and self.created_at >= timezone.now() - timedelta(minutes=10)

    def __str__(self):
        return f"Code for {self.email} ({'Used' if self.used else 'Unused'})"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username