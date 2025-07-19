from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from core.models import VaccineReminder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send pending vaccine reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what reminders would be sent without actually sending them',
        )
        parser.add_argument(
            '--email-only',
            action='store_true',
            help='Only send email reminders (skip SMS and push notifications)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        email_only = options['email_only']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting vaccine reminder check... (dry-run: {dry_run})')
        )
        
        # Buscar recordatorios pendientes
        pending_reminders = VaccineReminder.objects.filter(
            is_sent=False,
            is_active=True,
            reminder_date__lte=timezone.now()
        ).select_related('pet_vaccine', 'user', 'pet_vaccine__pet')
        
        if email_only:
            pending_reminders = pending_reminders.filter(notification_method='email')
        
        total_reminders = pending_reminders.count()
        self.stdout.write(f'Found {total_reminders} pending reminders')
        
        sent_count = 0
        failed_count = 0
        
        for reminder in pending_reminders:
            try:
                if self.send_reminder(reminder, dry_run):
                    sent_count += 1
                    if not dry_run:
                        reminder.mark_as_sent()
                else:
                    failed_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing reminder {reminder.id}: {str(e)}')
                )
                failed_count += 1
        
        # Resultados
        self.stdout.write(
            self.style.SUCCESS(
                f'Reminder processing complete:\n'
                f'  - Sent: {sent_count}\n'
                f'  - Failed: {failed_count}\n'
                f'  - Total: {total_reminders}'
            )
        )
    
    def send_reminder(self, reminder, dry_run=False):
        """Send a single reminder"""
        pet_name = reminder.pet_vaccine.pet.name
        vaccine_name = reminder.pet_vaccine.vaccine_name
        user_email = reminder.user.email
        
        self.stdout.write(f'Processing: {vaccine_name} for {pet_name} -> {user_email}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] Would send reminder'))
            return True
        
        try:
            if reminder.notification_method == 'email':
                return self.send_email_reminder(reminder)
            elif reminder.notification_method == 'sms':
                return self.send_sms_reminder(reminder)
            elif reminder.notification_method == 'push':
                return self.send_push_reminder(reminder)
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unknown notification method: {reminder.notification_method}')
                )
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send reminder: {str(e)}'))
            return False
    
    def send_email_reminder(self, reminder):
        """Send email reminder"""
        subject = f'Recordatorio de Vacuna - {reminder.pet_vaccine.pet.name}'
        
        # Usar mensaje personalizado o generar uno automático
        if reminder.message:
            message = reminder.message
        else:
            next_dose_date = reminder.pet_vaccine.next_dose_date.strftime('%d/%m/%Y')
            message = f'''
Hola,

Este es un recordatorio de que {reminder.pet_vaccine.pet.name} necesita la vacuna "{reminder.pet_vaccine.vaccine_name}".

Fecha programada: {next_dose_date}
Veterinario anterior: {reminder.pet_vaccine.veterinarian or 'No especificado'}

Por favor, programa una cita con tu veterinario.

Saludos,
Equipo PetFans
            '''.strip()
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reminder.user.email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Email sent to {reminder.user.email}')
            )
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email: {str(e)}')
            )
            return False
    
    def send_sms_reminder(self, reminder):
        """Send SMS reminder (placeholder - requires SMS service integration)"""
        self.stdout.write(
            self.style.WARNING('SMS reminders not implemented yet')
        )
        return False
    
    def send_push_reminder(self, reminder):
        """Send push notification (placeholder - requires push service integration)"""
        self.stdout.write(
            self.style.WARNING('Push notifications not implemented yet')
        )
        return False
