from django.contrib import admin
from .models import Pet, PetVaccine, VaccineReminder, LoginCode, Species, Breed, UserProfile


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


@admin.register(VaccineReminder)
class VaccineReminderAdmin(admin.ModelAdmin):
    list_display = ('pet_vaccine', 'user', 'reminder_type', 'reminder_date', 'is_sent', 'is_active', 'days_before')
    list_filter = ('reminder_type', 'notification_method', 'is_sent', 'is_active', 'created_at')
    search_fields = ('pet_vaccine__vaccine_name', 'pet_vaccine__pet__name', 'user__email', 'user__username')
    date_hierarchy = 'reminder_date'
    readonly_fields = ('is_sent', 'sent_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('pet_vaccine', 'user', 'reminder_type', 'notification_method')
        }),
        ('Configuración del Recordatorio', {
            'fields': ('reminder_date', 'days_before', 'message')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_sent', 'sent_at')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pet_vaccine', 'user', 'pet_vaccine__pet')