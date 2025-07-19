from django.contrib import admin
from .models import Pet, PetVaccine, LoginCode, Species, Breed, UserProfile


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'species')
    search_fields = ('name', 'species__name')
    list_filter = ('species',)


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'sex', 'get_owners')
    search_fields = ('name', 'species__name', 'breed__name', 'sex', 'description')
    list_filter = ('species', 'breed', 'sex')
    fields = ('name', 'species', 'breed', 'sex', 'birth_date', 'description', 'photo', 'owners')
    
    def get_owners(self, obj):
        return ", ".join([owner.username for owner in obj.owners.all()[:3]])
    get_owners.short_description = 'Owners'


@admin.register(PetVaccine)
class PetVaccineAdmin(admin.ModelAdmin):
    list_display = ('vaccine_name', 'pet', 'status', 'applied_date', 'next_dose_date', 'veterinarian')
    search_fields = ('vaccine_name', 'pet__name', 'veterinarian')
    list_filter = ('status', 'applied_date', 'next_dose_date')
    fields = ('pet', 'vaccine_name', 'status', 'applied_date', 'next_dose_date', 'veterinarian', 'notes')


@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'used', 'created_at')
    search_fields = ('email',)
    list_filter = ('used',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number')
    search_fields = ('user__username', 'full_name', 'phone_number')
    list_filter = ('user__is_active',)