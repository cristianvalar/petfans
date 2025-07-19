from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta, date
from decimal import Decimal
import uuid

from .models import (
    Species, Breed, Pet, PetVaccine, LoginCode, 
    UserProfile, VaccineReminder
)


class SpeciesModelTest(TestCase):
    """Tests para el modelo Species"""
    
    def setUp(self):
        self.species = Species.objects.create(name="Perro")
    
    def test_species_creation(self):
        """Test de creación básica de una especie"""
        self.assertEqual(self.species.name, "Perro")
        self.assertEqual(str(self.species), "Perro")
    
    def test_species_unique_constraint(self):
        """Test de que el nombre de especie debe ser único"""
        with self.assertRaises(IntegrityError):
            Species.objects.create(name="Perro")
    
    def test_species_verbose_names(self):
        """Test de los nombres verbosos del modelo"""
        self.assertEqual(Species._meta.verbose_name, "Species")
        self.assertEqual(Species._meta.verbose_name_plural, "Species")


class BreedModelTest(TestCase):
    """Tests para el modelo Breed"""
    
    def setUp(self):
        self.species_dog = Species.objects.create(name="Perro")
        self.species_cat = Species.objects.create(name="Gato")
        self.breed = Breed.objects.create(
            name="Golden Retriever",
            species=self.species_dog
        )
    
    def test_breed_creation(self):
        """Test de creación básica de una raza"""
        self.assertEqual(self.breed.name, "Golden Retriever")
        self.assertEqual(self.breed.species, self.species_dog)
        self.assertEqual(str(self.breed), "Golden Retriever (Perro)")
    
    def test_breed_unique_together_constraint(self):
        """Test de que no puede haber dos razas con el mismo nombre para la misma especie"""
        # Debería permitir la misma raza para diferente especie
        Breed.objects.create(name="Golden Retriever", species=self.species_cat)
        
        # No debería permitir la misma raza para la misma especie
        with self.assertRaises(IntegrityError):
            Breed.objects.create(name="Golden Retriever", species=self.species_dog)
    
    def test_breed_verbose_names(self):
        """Test de los nombres verbosos del modelo"""
        self.assertEqual(Breed._meta.verbose_name, "Breed")
        self.assertEqual(Breed._meta.verbose_name_plural, "Breeds")


class PetModelTest(TestCase):
    """Tests para el modelo Pet"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.species = Species.objects.create(name="Perro")
        self.breed = Breed.objects.create(name="Golden Retriever", species=self.species)
        
        self.pet = Pet.objects.create(
            name="Buddy",
            species=self.species,
            breed=self.breed,
            sex="Macho",
            birth_date=date(2020, 1, 15),
            description="Un perro muy amigable",
            chip_number="123456789",
            is_sterilized=True
        )
        self.pet.owners.add(self.user1, self.user2)
    
    def test_pet_creation(self):
        """Test de creación básica de una mascota"""
        self.assertEqual(self.pet.name, "Buddy")
        self.assertEqual(self.pet.species, self.species)
        self.assertEqual(self.pet.breed, self.breed)
        self.assertEqual(self.pet.sex, "Macho")
        self.assertEqual(self.pet.birth_date, date(2020, 1, 15))
        self.assertEqual(self.pet.description, "Un perro muy amigable")
        self.assertEqual(self.pet.chip_number, "123456789")
        self.assertTrue(self.pet.is_sterilized)
        self.assertEqual(self.pet.owners.count(), 2)
    
    def test_pet_uuid_primary_key(self):
        """Test de que el ID es un UUID válido"""
        self.assertIsInstance(self.pet.id, uuid.UUID)
    
    def test_pet_current_age_property(self):
        """Test de la propiedad current_age"""
        # Calcular edad esperada
        expected_age = (timezone.now().date() - self.pet.birth_date).days // 365
        self.assertEqual(self.pet.current_age, expected_age)
    
    def test_pet_current_age_without_birth_date(self):
        """Test de current_age cuando no hay fecha de nacimiento"""
        pet_no_birth = Pet.objects.create(
            name="Petty",
            species=self.species
        )
        self.assertIsNone(pet_no_birth.current_age)
    
    def test_pet_string_representation(self):
        """Test de la representación en string del modelo"""
        expected_str = f"Buddy - Perro - Golden Retriever (testuser1, testuser2)"
        self.assertEqual(str(self.pet), expected_str)
    
    def test_pet_string_representation_many_owners(self):
        """Test de string representation con muchos dueños"""
        user3 = User.objects.create_user(username='testuser3', email='test3@example.com')
        user4 = User.objects.create_user(username='testuser4', email='test4@example.com')
        user5 = User.objects.create_user(username='testuser5', email='test5@example.com')
        
        pet_many_owners = Pet.objects.create(name="ManyOwners", species=self.species)
        pet_many_owners.owners.add(self.user1, user3, user4, user5)
        
        expected_str = "ManyOwners - Perro (testuser1, testuser3, testuser4...)"
        self.assertEqual(str(pet_many_owners), expected_str)
    
    def test_pet_verbose_names(self):
        """Test de los nombres verbosos del modelo"""
        self.assertEqual(Pet._meta.verbose_name, "Pet")
        self.assertEqual(Pet._meta.verbose_name_plural, "Pets")


class PetVaccineModelTest(TestCase):
    """Tests para el modelo PetVaccine"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.species = Species.objects.create(name="Perro")
        self.pet = Pet.objects.create(name="Buddy", species=self.species)
        self.pet.owners.add(self.user)
        
        self.vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Triple",
            status='pending',
            applied_date=date(2023, 1, 15),
            next_dose_date=date(2024, 1, 15),
            veterinarian="Dr. García",
            notes="Primera dosis aplicada correctamente"
        )
    
    def test_vaccine_creation(self):
        """Test de creación básica de una vacuna"""
        self.assertEqual(self.vaccine.pet, self.pet)
        self.assertEqual(self.vaccine.vaccine_name, "Vacuna Triple")
        self.assertEqual(self.vaccine.status, 'pending')
        self.assertEqual(self.vaccine.applied_date, date(2023, 1, 15))
        self.assertEqual(self.vaccine.next_dose_date, date(2024, 1, 15))
        self.assertEqual(self.vaccine.veterinarian, "Dr. García")
        self.assertEqual(self.vaccine.notes, "Primera dosis aplicada correctamente")
    
    def test_vaccine_status_choices(self):
        """Test de las opciones de estado disponibles"""
        status_choices = [choice[0] for choice in PetVaccine.STATUS_CHOICES]
        expected_choices = ['pending', 'applied', 'overdue', 'scheduled']
        self.assertEqual(status_choices, expected_choices)
    
    def test_vaccine_string_representation(self):
        """Test de la representación en string del modelo"""
        expected_str = "Vacuna Triple - Buddy (Pendiente) - 15/01/2023"
        self.assertEqual(str(self.vaccine), expected_str)
    
    def test_vaccine_string_representation_no_applied_date(self):
        """Test de string representation sin fecha de aplicación"""
        vaccine_no_date = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Sin Fecha",
            status='pending'
        )
        expected_str = "Vacuna Sin Fecha - Buddy (Pendiente) - Sin fecha"
        self.assertEqual(str(vaccine_no_date), expected_str)
    
    def test_vaccine_is_overdue_property(self):
        """Test de la propiedad is_overdue"""
        # Vacuna con fecha futura no está vencida
        future_vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Futura",
            status='pending',
            next_dose_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertFalse(future_vaccine.is_overdue)
        
        # Vacuna con fecha pasada está vencida
        past_vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Pasada",
            status='pending',
            next_dose_date=timezone.now().date() - timedelta(days=30)
        )
        self.assertTrue(past_vaccine.is_overdue)
        
        # Vacuna aplicada no está vencida aunque tenga fecha pasada
        applied_vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Aplicada",
            status='applied',
            next_dose_date=timezone.now().date() - timedelta(days=30)
        )
        self.assertFalse(applied_vaccine.is_overdue)
    
    def test_vaccine_mark_as_applied(self):
        """Test del método mark_as_applied"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna para Marcar",
            status='pending'
        )
        
        vaccine.mark_as_applied()
        vaccine.refresh_from_db()
        
        self.assertEqual(vaccine.status, 'applied')
        self.assertEqual(vaccine.applied_date, timezone.now().date())
    
    def test_vaccine_mark_as_applied_with_date(self):
        """Test del método mark_as_applied con fecha específica"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna con Fecha",
            status='pending'
        )
        
        custom_date = date(2023, 6, 15)
        vaccine.mark_as_applied(custom_date)
        vaccine.refresh_from_db()
        
        self.assertEqual(vaccine.status, 'applied')
        self.assertEqual(vaccine.applied_date, custom_date)
    
    def test_vaccine_verbose_names(self):
        """Test de los nombres verbosos del modelo"""
        self.assertEqual(PetVaccine._meta.verbose_name, "Vacuna de Mascota")
        self.assertEqual(PetVaccine._meta.verbose_name_plural, "Vacunas de Mascotas")
    
    def test_vaccine_ordering(self):
        """Test del ordenamiento por defecto"""
        vaccine1 = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna 1",
            applied_date=date(2023, 1, 1)
        )
        vaccine2 = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna 2",
            applied_date=date(2023, 2, 1)
        )
        
        vaccines = list(PetVaccine.objects.all())
        # Debería estar ordenado por applied_date descendente
        # El orden es: vaccine2 (feb), vaccine1 (ene), self.vaccine (ene 2023)
        self.assertEqual(vaccines[0], vaccine2)
        self.assertEqual(vaccines[1], self.vaccine)
        self.assertEqual(vaccines[2], vaccine1)


class LoginCodeModelTest(TestCase):
    """Tests para el modelo LoginCode"""
    
    def setUp(self):
        self.login_code = LoginCode.objects.create(
            email='test@example.com',
            code='123456'
        )
    
    def test_login_code_creation(self):
        """Test de creación básica de un código de login"""
        self.assertEqual(self.login_code.email, 'test@example.com')
        self.assertEqual(self.login_code.code, '123456')
        self.assertFalse(self.login_code.used)
        self.assertIsNotNone(self.login_code.created_at)
    
    def test_login_code_string_representation(self):
        """Test de la representación en string del modelo"""
        self.assertEqual(str(self.login_code), "Code for test@example.com (Unused)")
        
        self.login_code.used = True
        self.login_code.save()
        self.assertEqual(str(self.login_code), "Code for test@example.com (Used)")
    
    def test_login_code_is_valid_fresh(self):
        """Test de validez de un código recién creado"""
        self.assertTrue(self.login_code.is_valid())
    
    def test_login_code_is_valid_used(self):
        """Test de validez de un código usado"""
        self.login_code.used = True
        self.login_code.save()
        self.assertFalse(self.login_code.is_valid())
    
    def test_login_code_is_valid_expired(self):
        """Test de validez de un código expirado"""
        # Crear un código con fecha antigua
        old_code = LoginCode.objects.create(
            email='old@example.com',
            code='654321'
        )
        # Simular que fue creado hace 11 minutos
        old_code.created_at = timezone.now() - timedelta(minutes=11)
        old_code.save()
        
        self.assertFalse(old_code.is_valid())
    
    def test_login_code_verbose_names(self):
        """Test de los nombres verbosos del modelo"""
        self.assertEqual(LoginCode._meta.verbose_name, "Login Code")
        self.assertEqual(LoginCode._meta.verbose_name_plural, "Login Codes")


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name='Juan Pérez',
            phone_number='+34612345678'
        )
    
    def test_user_profile_creation(self):
        """Test de creación básica de un perfil de usuario"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.full_name, 'Juan Pérez')
        self.assertEqual(self.profile.phone_number, '+34612345678')
        # El campo avatar puede ser None o una cadena vacía, pero no es None literal
        self.assertFalse(self.profile.avatar)
    
    def test_user_profile_string_representation(self):
        """Test de la representación en string del modelo"""
        self.assertEqual(str(self.profile), 'Juan Pérez')
        
        # Test sin full_name - crear un nuevo usuario para evitar conflictos
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        profile_no_name = UserProfile.objects.create(user=user2)
        self.assertEqual(str(profile_no_name), 'testuser2')
    
    def test_user_profile_one_to_one_relationship(self):
        """Test de la relación one-to-one con User"""
        # No debería poder crear otro perfil para el mismo usuario
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user)


class VaccineReminderModelTest(TestCase):
    """Tests para el modelo VaccineReminder"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.species = Species.objects.create(name="Perro")
        self.pet = Pet.objects.create(name="Buddy", species=self.species)
        self.pet.owners.add(self.user)
        
        # Crear vacuna sin next_dose_date para evitar creación automática de recordatorios
        self.vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Triple",
            status='pending',
            applied_date=date(2023, 1, 15),
            veterinarian="Dr. García",
            notes="Primera dosis aplicada correctamente"
        )
        
        # Crear recordatorio manualmente con valores únicos
        self.reminder = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='upcoming',
            reminder_date=timezone.now() + timedelta(days=7),
            notification_method='email',
            days_before=10,  # Cambiar a 10 para evitar conflictos
            message="Recordatorio personalizado"
        )
    
    def test_reminder_creation(self):
        """Test de creación básica de un recordatorio"""
        self.assertEqual(self.reminder.pet_vaccine, self.vaccine)
        self.assertEqual(self.reminder.user, self.user)
        self.assertEqual(self.reminder.reminder_type, 'upcoming')
        self.assertEqual(self.reminder.notification_method, 'email')
        self.assertEqual(self.reminder.days_before, 10)  # Cambiado a 10
        self.assertFalse(self.reminder.is_sent)
        self.assertIsNone(self.reminder.sent_at)
        self.assertTrue(self.reminder.is_active)
        self.assertEqual(self.reminder.message, "Recordatorio personalizado")
    
    def test_reminder_type_choices(self):
        """Test de las opciones de tipo de recordatorio"""
        reminder_types = [choice[0] for choice in VaccineReminder.REMINDER_TYPE_CHOICES]
        expected_types = ['upcoming', 'overdue', 'scheduled']
        self.assertEqual(reminder_types, expected_types)
    
    def test_notification_method_choices(self):
        """Test de las opciones de método de notificación"""
        notification_methods = [choice[0] for choice in VaccineReminder.NOTIFICATION_METHOD_CHOICES]
        expected_methods = ['email', 'push', 'sms']
        self.assertEqual(notification_methods, expected_methods)
    
    def test_reminder_string_representation(self):
        """Test de la representación en string del modelo"""
        expected_str = f"Próxima vacuna: Vacuna Triple para Buddy - {self.reminder.reminder_date.strftime('%d/%m/%Y')}"
        self.assertEqual(str(self.reminder), expected_str)
    
    def test_reminder_is_due_property(self):
        """Test de la propiedad is_due"""
        # Recordatorio futuro no está vencido
        future_reminder = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='overdue',
            reminder_date=timezone.now() + timedelta(days=1),
            notification_method='email',
            days_before=5
        )
        self.assertFalse(future_reminder.is_due)
        
        # Recordatorio pasado está vencido
        past_reminder = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='scheduled',
            reminder_date=timezone.now() - timedelta(days=1),
            notification_method='email',
            days_before=3
        )
        self.assertTrue(past_reminder.is_due)
        
        # Recordatorio enviado no está vencido aunque tenga fecha pasada
        sent_reminder = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='upcoming',
            reminder_date=timezone.now() - timedelta(days=1),
            notification_method='email',
            days_before=2,
            is_sent=True
        )
        self.assertFalse(sent_reminder.is_due)
        
        # Recordatorio inactivo no está vencido
        inactive_reminder = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='overdue',
            reminder_date=timezone.now() - timedelta(days=1),
            notification_method='email',
            days_before=1,
            is_active=False
        )
        self.assertFalse(inactive_reminder.is_due)
    
    def test_reminder_mark_as_sent(self):
        """Test del método mark_as_sent"""
        reminder = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='scheduled',
            reminder_date=timezone.now(),
            notification_method='email',
            days_before=4
        )
        
        reminder.mark_as_sent()
        reminder.refresh_from_db()
        
        self.assertTrue(reminder.is_sent)
        self.assertIsNotNone(reminder.sent_at)
    
    def test_reminder_calculate_reminder_date(self):
        """Test del método calculate_reminder_date"""
        # Crear una vacuna con next_dose_date para este test
        vaccine_with_date = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna con Fecha",
            status='pending',
            next_dose_date=date(2024, 6, 15)
        )
        
        reminder = VaccineReminder.objects.create(
            pet_vaccine=vaccine_with_date,
            user=self.user,
            reminder_type='upcoming',
            reminder_date=timezone.now(),
            notification_method='email',
            days_before=10
        )
        
        reminder.calculate_reminder_date()
        reminder.refresh_from_db()
        
        expected_date = vaccine_with_date.next_dose_date - timedelta(days=10)
        self.assertEqual(reminder.reminder_date.date(), expected_date)
    
    def test_reminder_unique_together_constraint(self):
        """Test de la constraint unique_together"""
        # No debería poder crear otro recordatorio con los mismos valores
        with self.assertRaises(IntegrityError):
            VaccineReminder.objects.create(
                pet_vaccine=self.vaccine,
                user=self.user,
                reminder_type='upcoming',
                reminder_date=timezone.now(),
                notification_method='email',
                days_before=10  # Cambiar a 10 para que coincida con el setUp
            )
    
    def test_reminder_verbose_names(self):
        """Test de los nombres verbosos del modelo"""
        self.assertEqual(VaccineReminder._meta.verbose_name, "Recordatorio de Vacuna")
        self.assertEqual(VaccineReminder._meta.verbose_name_plural, "Recordatorios de Vacunas")
    
    def test_reminder_ordering(self):
        """Test del ordenamiento por defecto"""
        # Crear recordatorios con fechas fijas para evitar problemas de timing
        base_date = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        
        reminder1 = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='upcoming',
            reminder_date=base_date + timedelta(days=1),
            notification_method='email',
            days_before=6
        )
        reminder2 = VaccineReminder.objects.create(
            pet_vaccine=self.vaccine,
            user=self.user,
            reminder_type='overdue',
            reminder_date=base_date,
            notification_method='email',
            days_before=8
        )
        
        reminders = list(VaccineReminder.objects.all())
        # Debería estar ordenado por reminder_date ascendente
        # El orden es: reminder2 (base_date), reminder1 (base_date+1), self.reminder (base_date+7)
        self.assertEqual(reminders[0], reminder2)
        self.assertEqual(reminders[1], reminder1)
        self.assertEqual(reminders[2], self.reminder)


class VaccineReminderAutomaticCreationTest(TestCase):
    """Tests para la creación automática de recordatorios"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.species = Species.objects.create(name="Perro")
        self.pet = Pet.objects.create(name="Buddy", species=self.species)
        self.pet.owners.add(self.user)
    
    def test_create_automatic_reminders_with_next_dose_date(self):
        """Test de creación automática de recordatorios con fecha de próxima dosis"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Triple",
            status='pending',
            next_dose_date=date(2024, 1, 15)
        )
        
        # Verificar que se crearon los recordatorios automáticos
        reminders = VaccineReminder.objects.filter(pet_vaccine=vaccine)
        self.assertEqual(reminders.count(), 2)
        
        # Verificar recordatorio de 7 días
        reminder_7 = reminders.filter(days_before=7).first()
        self.assertIsNotNone(reminder_7)
        self.assertEqual(reminder_7.reminder_type, 'upcoming')
        self.assertEqual(reminder_7.notification_method, 'email')
        self.assertEqual(reminder_7.user, self.user)
        
        # Verificar recordatorio de 1 día
        reminder_1 = reminders.filter(days_before=1).first()
        self.assertIsNotNone(reminder_1)
        self.assertEqual(reminder_1.reminder_type, 'upcoming')
        self.assertEqual(reminder_1.notification_method, 'email')
        self.assertEqual(reminder_1.user, self.user)
    
    def test_create_automatic_reminders_without_next_dose_date(self):
        """Test de que no se crean recordatorios sin fecha de próxima dosis"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Sin Fecha",
            status='pending'
        )
        
        reminders = VaccineReminder.objects.filter(pet_vaccine=vaccine)
        self.assertEqual(reminders.count(), 0)
    
    def test_create_automatic_reminders_multiple_owners(self):
        """Test de creación de recordatorios para múltiples dueños"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.pet.owners.add(user2)
        
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Múltiples Dueños",
            status='pending',
            next_dose_date=date(2024, 1, 15)
        )
        
        # Verificar que se crearon recordatorios para ambos dueños
        reminders = VaccineReminder.objects.filter(pet_vaccine=vaccine)
        self.assertEqual(reminders.count(), 4)  # 2 recordatorios por 2 dueños
        
        user_reminders = reminders.filter(user=self.user)
        user2_reminders = reminders.filter(user=user2)
        self.assertEqual(user_reminders.count(), 2)
        self.assertEqual(user2_reminders.count(), 2)
    
    def test_create_automatic_reminders_applied_status(self):
        """Test de que no se crean recordatorios para vacunas aplicadas"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Aplicada",
            status='applied',
            next_dose_date=date(2024, 1, 15)
        )
        
        reminders = VaccineReminder.objects.filter(pet_vaccine=vaccine)
        self.assertEqual(reminders.count(), 0)
    
    def test_create_automatic_reminders_get_or_create_behavior(self):
        """Test de que get_or_create evita duplicados"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna Duplicada",
            status='pending',
            next_dose_date=date(2024, 1, 15)
        )
        
        # Llamar save() nuevamente para simular una actualización
        vaccine.save()
        
        reminders = VaccineReminder.objects.filter(pet_vaccine=vaccine)
        self.assertEqual(reminders.count(), 2)  # No debería crear duplicados


class ModelIntegrationTest(TestCase):
    """Tests de integración entre modelos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.species = Species.objects.create(name="Perro")
        self.breed = Breed.objects.create(name="Golden Retriever", species=self.species)
        self.pet = Pet.objects.create(
            name="Buddy",
            species=self.species,
            breed=self.breed,
            birth_date=date(2020, 1, 15)
        )
        self.pet.owners.add(self.user)
    
    def test_pet_vaccine_reminder_integration(self):
        """Test de integración entre Pet, PetVaccine y VaccineReminder"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna de Integración",
            status='pending',
            next_dose_date=date(2024, 1, 15)
        )
        
        # Verificar que se creó la vacuna
        self.assertEqual(vaccine.pet, self.pet)
        
        # Verificar que se crearon los recordatorios automáticos
        reminders = VaccineReminder.objects.filter(pet_vaccine=vaccine)
        self.assertEqual(reminders.count(), 2)
        
        # Verificar que los recordatorios están asociados al usuario correcto
        for reminder in reminders:
            self.assertEqual(reminder.user, self.user)
            self.assertEqual(reminder.pet_vaccine, vaccine)
    
    def test_cascade_deletion(self):
        """Test de eliminación en cascada"""
        vaccine = PetVaccine.objects.create(
            pet=self.pet,
            vaccine_name="Vacuna para Eliminar",
            status='pending',
            next_dose_date=date(2024, 1, 15)
        )
        
        # Verificar que se crearon recordatorios
        self.assertEqual(VaccineReminder.objects.filter(pet_vaccine=vaccine).count(), 2)
        
        # Guardar el ID antes de eliminar
        vaccine_id = vaccine.id
        
        # Eliminar la vacuna
        vaccine.delete()
        
        # Verificar que se eliminaron los recordatorios usando el ID
        self.assertEqual(VaccineReminder.objects.filter(pet_vaccine_id=vaccine_id).count(), 0)
    
    def test_protect_deletion_species(self):
        """Test de protección contra eliminación de especies con mascotas"""
        # Intentar eliminar una especie que tiene mascotas debería fallar
        with self.assertRaises(IntegrityError):
            self.species.delete()
        
        # Eliminar la mascota primero
        self.pet.delete()
        
        # Ahora debería poder eliminar la especie
        self.species.delete()
        self.assertEqual(Species.objects.count(), 0)
