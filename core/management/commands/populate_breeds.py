from django.core.management.base import BaseCommand
from core.models import Species, Breed

class Command(BaseCommand):
    help = 'Popula la base de datos con una lista extensa de razas de perros y gatos'

    def handle(self, *args, **options):
        # 1. Definir Especies
        dog_species, _ = Species.objects.get_or_create(name='Perro')
        cat_species, _ = Species.objects.get_or_create(name='Gato')

        # 2. Listado de razas de Perros (Ordenadas alfabéticamente)
        # "Mestizo" se maneja aparte para que sea la primera
        dog_breeds = [
            "Afgano", "Akita Inu", "Alano Español", "Alaskan Malamute", "American Stanford",
            "Australian Shepherd", "Basenji", "Basset Hound", "Beagle", "Bichón Frisé",
            "Bichón Maltés", "Bloodhound", "Bobtail", "Border Collie", "Borzoi",
            "Boston Terrier", "Boxer", "Boyero de Berna", "Braco Alemán", "Bretón",
            "Bulldog Americano", "Bulldog Francés", "Bulldog Inglés", "Bull Terrier", 
            "Bullmastiff", "Caniche (Poodle)", "Carlino (Pug)", "Cavalier King Charles",
            "Chihuahua", "Chow Chow", "Cocker Spaniel", "Collie", "Corgi", "Dachshund (Salchicha)",
            "Dálmata", "Doberman", "Dogo Argentino", "Dogo Alemán", "Dogo de Burdeos",
            "Fox Terrier", "Galgo", "Golden Retriever", "Greyhound", "Husky Siberiano",
            "Jack Russell", "Labrador Retriever", "Mastín Español", "Mastín Napolitano",
            "Papillón", "Pastor Alemán", "Pastor Belga", "Pastor de Shetland", "Pequinés",
            "Pinscher", "Pit Bull", "Pointer", "Pomerania", "Presa Canario", "Rottweiler",
            "Samoyedo", "San Bernardo", "Schnauzer", "Setter Inglés", "Setter Irlandés",
            "Shiba Inu", "Shih Tzu", "Staffordshire Bull Terrier", "Terranova", "Weimaraner",
            "West Highland White Terrier", "Yorkshire Terrier"
        ]

        # 3. Listado de razas de Gatos (Ordenadas alfabéticamente)
        cat_breeds = [
            "Abisinio", "American Shorthair", "Angora Turco", "Azul Ruso", "Balinés",
            "Bengalí", "Birmano", "Bobtail Japonés", "Bombay", "British Shorthair",
            "Burmés", "Chartreux", "Cornish Rex", "Devon Rex", "Exótico de pelo corto",
            "Habana Brown", "Himalayo", "Javanés", "Korat", "Maine Coon", "Manx",
            "Mau Egipcio", "Munchkin", "Nebelung", "Noruego de Bosque", "Ocicat",
            "Oriental", "Persa", "Ragdoll", "Savannah", "Scottish Fold", "Selkirk Rex",
            "Siamés", "Siberiano", "Snowshoe", "Somalí", "Sphynx (Esfinge)", "Tonquinés",
            "Van Turco"
        ]

        # Función para poblar
        def populate_species_breeds(species_obj, breed_list):
            self.stdout.write(f'Poblando razas para: {species_obj.name}...')
            
            # Asegurar primero "Mestizo"
            Breed.objects.get_or_create(name='Mestizo', species=species_obj)
            
            # Agregar el resto
            count = 0
            for breed_name in sorted(breed_list):
                _, created = Breed.objects.get_or_create(name=breed_name, species=species_obj)
                if created:
                    count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Finalizado: {count} nuevas razas agregadas a {species_obj.name}'))

        # Ejecutar poblado
        populate_species_breeds(dog_species, dog_breeds)
        populate_species_breeds(cat_species, cat_breeds)

        self.stdout.write(self.style.SUCCESS('¡Base de datos de razas actualizada correctamente!'))
