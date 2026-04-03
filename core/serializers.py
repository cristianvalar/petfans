from rest_framework import serializers
from .models import Species, Breed, Pet, UserProfile, PetVaccine, LoginCode, VaccineReminder, PetUser, PetWeight
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
        read_only_fields = ['created_at', 'updated_at']


class PetWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetWeight
        fields = ['id', 'pet', 'weight', 'date', 'created_at']
        read_only_fields = ['created_at']


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class PetCollaboratorSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    full_name = serializers.ReadOnlyField(source='user.profile.full_name')
    avatar = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = PetUser
        fields = ['user_id', 'email', 'full_name', 'avatar', 'role', 'role_display']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.user.profile.avatar and hasattr(obj.user.profile.avatar, 'url'):
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None


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
    care_team = PetCollaboratorSerializer(source='user_relationships', many=True, read_only=True)

    image_url = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    last_weight = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'species', 'species_id', 'breed', 'breed_id', 'sex',
            'birth_date', 'description', 'photo', 'image_url', 'chip_number', 'is_sterilized',
            'current_age', 'care_team', 'user_role', 'last_weight', 'is_active', 'created_at', 'updated_at', 'vaccines'
        ]
        read_only_fields = ['is_active', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            return request.build_absolute_uri(obj.photo.url)
        return None

    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            relationship = obj.user_relationships.filter(user=request.user).first()
            if relationship:
                return relationship.role
        return None

    def update(self, instance, validated_data):
        """Prevent owners M2M from being modified through the main pet update endpoint."""
        validated_data.pop('owners', None)
        return super().update(instance, validated_data)

    def get_last_weight(self, obj):
        last_weight = obj.weights.first()
        if last_weight:
            return {
                'weight': last_weight.weight,
                'date': last_weight.date
            }
        return None


class LoginCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginCode
        fields = ['id', 'email', 'code', 'used', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'full_name', 'phone_number', 'avatar', 'is_premium', 'country']
        read_only_fields = ['is_premium']


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