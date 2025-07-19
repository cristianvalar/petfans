from rest_framework import serializers
from .models import Species, Breed, Pet, UserProfile, PetVaccine, LoginCode, VaccineReminder
from django.contrib.auth.models import User


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name']


class BreedSerializer(serializers.ModelSerializer):
    species = SpeciesSerializer(read_only=True)
    species_id = serializers.PrimaryKeyRelatedField(
        queryset=Species.objects.all(),
        source='species',
        write_only=True
    )

    class Meta:
        model = Breed
        fields = ['id', 'name', 'species', 'species_id']


class PetVaccineSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = PetVaccine
        fields = [
            'id', 'pet', 'pet_name', 'vaccine_name', 'status', 'status_display', 
            'applied_date', 'next_dose_date', 'veterinarian', 'notes', 
            'is_overdue', 'created_at', 'updated_at'
        ]


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class PetSerializer(serializers.ModelSerializer):
    current_age = serializers.ReadOnlyField()
    species = SpeciesSerializer(read_only=True)
    species_id = serializers.PrimaryKeyRelatedField(
        queryset=Species.objects.all(),
        source='species',
        write_only=True
    )
    breed = BreedSerializer(read_only=True)
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(),
        source='breed',
        write_only=True,
        required=False,
        allow_null=True 
    )
    vaccines = PetVaccineSerializer(many=True, read_only=True)
    owners = BasicUserSerializer(many=True, read_only=True)
    owners_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='owners',
        many=True,
        write_only=True
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'species', 'species_id', 'breed', 'breed_id', 'sex',
            'birth_date', 'description', 'photo', 'image_url', 'chip_number', 'is_sterilized',
            'current_age', 'owners', 'owners_id', 'created_at', 'updated_at', 'vaccines'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            return request.build_absolute_uri(obj.photo.url)
        return None


class LoginCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginCode
        fields = ['id', 'email', 'code', 'used', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'avatar']


class VaccineReminderSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet_vaccine.pet.name', read_only=True)
    vaccine_name = serializers.CharField(source='pet_vaccine.vaccine_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    notification_method_display = serializers.CharField(source='get_notification_method_display', read_only=True)
    is_due = serializers.ReadOnlyField()

    class Meta:
        model = VaccineReminder
        fields = [
            'id', 'pet_vaccine', 'user', 'pet_name', 'vaccine_name', 'user_email',
            'reminder_type', 'reminder_type_display', 'reminder_date', 
            'notification_method', 'notification_method_display', 'days_before',
            'is_sent', 'sent_at', 'is_active', 'message', 'is_due',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_sent', 'sent_at']