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
    


class PetVaccine(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('applied', 'Aplicada'),
        ('overdue', 'Vencida'),
        ('scheduled', 'Programada'),
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='vaccines')
    vaccine_name = models.CharField(max_length=255, verbose_name='Nombre de la vacuna')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    applied_date = models.DateField(null=True, blank=True, verbose_name='Fecha de aplicación')
    next_dose_date = models.DateField(null=True, blank=True, verbose_name='Próxima dosis')
    veterinarian = models.CharField(max_length=255, blank=True, null=True, verbose_name='Veterinario')
    notes = models.TextField(blank=True, null=True, verbose_name='Notas adicionales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vacuna de Mascota"
        verbose_name_plural = "Vacunas de Mascotas"
        ordering = ['-applied_date', '-created_at']

    def __str__(self):
        status_display = self.get_status_display()
        date_str = self.applied_date.strftime('%d/%m/%Y') if self.applied_date else 'Sin fecha'
        return f"{self.vaccine_name} - {self.pet.name} ({status_display}) - {date_str}"
    
    @property
    def is_overdue(self):
        """Verifica si la vacuna está vencida"""
        if self.next_dose_date and self.status in ['pending', 'scheduled']:
            return timezone.now().date() > self.next_dose_date
        return False
    
    def mark_as_applied(self, applied_date=None):
        """Marca la vacuna como aplicada"""
        self.status = 'applied'
        self.applied_date = applied_date or timezone.now().date()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save para crear recordatorios automáticamente"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Crear recordatorios automáticos si hay fecha de próxima dosis
        if self.next_dose_date and self.status in ['pending', 'scheduled']:
            # Importar aquí para evitar importación circular
            VaccineReminder.create_automatic_reminders(self)


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


class VaccineReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('upcoming', 'Próxima vacuna'),
        ('overdue', 'Vacuna vencida'),
        ('scheduled', 'Vacuna programada'),
    ]
    
    NOTIFICATION_METHOD_CHOICES = [
        ('email', 'Correo electrónico'),
        ('push', 'Notificación push'),
        ('sms', 'SMS'),
    ]
    
    pet_vaccine = models.ForeignKey(PetVaccine, on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vaccine_reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name='Tipo de recordatorio')
    reminder_date = models.DateTimeField(verbose_name='Fecha del recordatorio')
    notification_method = models.CharField(max_length=10, choices=NOTIFICATION_METHOD_CHOICES, default='email', verbose_name='Método de notificación')
    days_before = models.IntegerField(default=7, verbose_name='Días de anticipación')
    is_sent = models.BooleanField(default=False, verbose_name='Enviado')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de envío')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    message = models.TextField(blank=True, null=True, verbose_name='Mensaje personalizado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recordatorio de Vacuna"
        verbose_name_plural = "Recordatorios de Vacunas"
        ordering = ['reminder_date', '-created_at']
        unique_together = ['pet_vaccine', 'user', 'reminder_type', 'days_before']

    def __str__(self):
        vaccine_name = self.pet_vaccine.vaccine_name
        pet_name = self.pet_vaccine.pet.name
        reminder_type_display = self.get_reminder_type_display()
        return f"{reminder_type_display}: {vaccine_name} para {pet_name} - {self.reminder_date.strftime('%d/%m/%Y')}"
    
    @property
    def is_due(self):
        """Verifica si el recordatorio debe ser enviado"""
        return timezone.now() >= self.reminder_date and not self.is_sent and self.is_active
    
    def mark_as_sent(self):
        """Marca el recordatorio como enviado"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()
    
    def calculate_reminder_date(self):
        """Calcula la fecha del recordatorio basado en la próxima dosis"""
        if self.pet_vaccine.next_dose_date:
            reminder_date = self.pet_vaccine.next_dose_date - timedelta(days=self.days_before)
            # Convertir a datetime para almacenar en reminder_date
            self.reminder_date = timezone.make_aware(
                timezone.datetime.combine(reminder_date, timezone.datetime.min.time())
            )
            self.save()
    
    @classmethod
    def create_automatic_reminders(cls, pet_vaccine):
        """Crea recordatorios automáticos para una vacuna"""
        if not pet_vaccine.next_dose_date:
            return
        
        # Crear recordatorios para todos los dueños de la mascota
        for owner in pet_vaccine.pet.owners.all():
            # Recordatorio 7 días antes
            cls.objects.get_or_create(
                pet_vaccine=pet_vaccine,
                user=owner,
                reminder_type='upcoming',
                days_before=7,
                defaults={
                    'notification_method': 'email',
                    'message': f"Recordatorio: {pet_vaccine.vaccine_name} para {pet_vaccine.pet.name} vence pronto."
                }
            )
            
            # Recordatorio 1 día antes
            cls.objects.get_or_create(
                pet_vaccine=pet_vaccine,
                user=owner,
                reminder_type='upcoming',
                days_before=1,
                defaults={
                    'notification_method': 'email',
                    'message': f"¡Urgente! {pet_vaccine.vaccine_name} para {pet_vaccine.pet.name} vence mañana."
                }
            )