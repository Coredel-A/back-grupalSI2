from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from datetime import datetime, timedelta
from django.utils import timezone
import json

# Importar todos los modelos
from a_usuarios.models import Usuario
from a_roles.models import Rol
from a_pacientes.models import Pacientes
from a_sucursales.models import Establecimiento, SucursalEspecialidad
from a_especialidades.models import Especialidad
from a_historiales.models import HistorialClinico, Formulario, Pregunta, Respuesta

fake = Faker('es_ES')  # Configurar Faker para español

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuarios',
            type=int,
            default=20,
            help='Número de usuarios a crear'
        )
        parser.add_argument(
            '--pacientes',
            type=int,
            default=50,
            help='Número de pacientes a crear'
        )
        parser.add_argument(
            '--establecimientos',
            type=int,
            default=10,
            help='Número de establecimientos a crear'
        )
        parser.add_argument(
            '--historiales',
            type=int,
            default=100,
            help='Número de historiales clínicos a crear'
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS('Iniciando población de la base de datos...'))
            
            
            # Crear especialidades médicas
            self.create_especialidades()
            
            # Crear establecimientos
            self.create_establecimientos(options['establecimientos'])
            
            # Crear usuarios
            self.create_usuarios(options['usuarios'])
            
            # Crear pacientes
            self.create_pacientes(options['pacientes'])
            
            # Crear formularios y preguntas
            self.create_formularios_y_preguntas()
            
            # Crear historiales clínicos
            self.create_historiales_clinicos(options['historiales'])
            
            self.stdout.write(self.style.SUCCESS('Base de datos poblada exitosamente!'))

    def create_especialidades(self):
        """Crear especialidades médicas"""
        especialidades = [
            ('Cardiología', 'Especialidad médica que se encarga del estudio, diagnóstico y tratamiento de las enfermedades del corazón'),
            ('Neurología', 'Especialidad médica que se ocupa de las enfermedades del sistema nervioso'),
            ('Pediatría', 'Rama de la medicina que se especializa en la salud y las enfermedades de los niños'),
            ('Ginecología', 'Especialidad médica que se encarga del cuidado del sistema reproductor femenino'),
            ('Traumatología', 'Especialidad médica que se dedica al estudio de las lesiones del aparato locomotor'),
            ('Dermatología', 'Especialidad médica que se encarga del estudio de la estructura y función de la piel'),
            ('Oftalmología', 'Especialidad médica que estudia las enfermedades de los ojos'),
            ('Otorrinolaringología', 'Especialidad médica que se encarga de las enfermedades del oído, nariz y garganta'),
            ('Psiquiatría', 'Especialidad médica dedicada al estudio, prevención, diagnóstico y tratamiento de los trastornos mentales'),
            ('Medicina Interna', 'Especialidad médica que se dedica a la atención integral del adulto enfermo'),
            ('Cirugía General', 'Especialidad médica que se encarga de realizar procedimientos quirúrgicos'),
            ('Anestesiología', 'Especialidad médica que se encarga de proporcionar anestesia y cuidados perioperatorios'),
        ]
        
        for nombre, descripcion in especialidades:
            especialidad, created = Especialidad.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f'Especialidad creada: {nombre}')

    def create_establecimientos(self, count):
        """Crear establecimientos de salud en Bolivia"""
        ciudades_bolivia = [
            'La Paz', 'Santa Cruz de la Sierra', 'Cochabamba', 'Oruro', 'Potosí',
            'Tarija', 'Sucre', 'Trinidad', 'Cobija', 'Riberalta', 'Montero',
            'El Alto', 'Quillacollo', 'Sacaba', 'Viacha'
        ]
        
        tipos_establecimiento = ['hospital', 'clinica', 'consultorio', 'centro_salud', 'laboratorio']
        niveles = ['nivel_1', 'nivel_2', 'nivel_3']
        
        especialidades = list(Especialidad.objects.all())
        
        for i in range(count):
            ciudad = random.choice(ciudades_bolivia)
            tipo = random.choice(tipos_establecimiento)
            
            # Generar nombre según el tipo
            if tipo == 'hospital':
                nombre = f"Hospital {fake.last_name()} - {ciudad}"
            elif tipo == 'clinica':
                nombre = f"Clínica {fake.company()} - {ciudad}"
            elif tipo == 'consultorio':
                nombre = f"Consultorio Dr. {fake.last_name()} - {ciudad}"
            elif tipo == 'centro_salud':
                nombre = f"Centro de Salud {fake.street_name()} - {ciudad}"
            else:
                nombre = f"Laboratorio {fake.company()} - {ciudad}"
            
            establecimiento = Establecimiento.objects.create(
                nombre=nombre,
                direccion=f"{fake.street_address()}, {ciudad}, Bolivia",
                telefono=fake.phone_number()[:15],
                correo=fake.email(),
                tipo_establecimiento=tipo,
                nivel=random.choice(niveles)
            )
            
            # Asignar especialidades aleatorias al establecimiento
            num_especialidades = random.randint(2, 6)
            especialidades_seleccionadas = random.sample(especialidades, min(num_especialidades, len(especialidades)))
            
            for especialidad in especialidades_seleccionadas:
                SucursalEspecialidad.objects.create(
                    sucursal=establecimiento,
                    especialidad=especialidad
                )
            
            self.stdout.write(f'Establecimiento creado: {nombre}')

    def create_usuarios(self, count):
        """Crear usuarios del sistema"""
        roles = list(Rol.objects.all())
        especialidades = list(Especialidad.objects.all())
        establecimientos = list(Establecimiento.objects.all())
        
        for i in range(count):
            nombre = fake.first_name()
            apellido = fake.last_name()
            email = f"{nombre.lower()}.{apellido.lower()}@hospital.bo"
            
            rol = random.choice(roles)
            
            # Asignar especialidad solo a doctores y residentes
            especialidad = None
            if rol.nombre in ['Doctor', 'Jefe de Especialidad', 'Residente']:
                especialidad = random.choice(especialidades)
            
            usuario = Usuario.objects.create_user(
                email=email,
                nombre=nombre,
                apellido=apellido,
                password='password123',  # Contraseña por defecto
                fecha_nacimiento=fake.date_of_birth(minimum_age=25, maximum_age=65),
                especialidad=especialidad,
                establecimiento=random.choice(establecimientos) if establecimientos else None,
                rol=rol
            )
            
            self.stdout.write(f'Usuario creado: {nombre} {apellido} - {rol.nombre}')

    def create_pacientes(self, count):
        """Crear pacientes"""
        for i in range(count):
            nombre = fake.first_name()
            apellido = fake.last_name()
            
            # Generar CI boliviano (formato aproximado)
            ci = f"{random.randint(1000000, 9999999)}-{random.choice(['LP', 'SC', 'CB', 'OR', 'PT', 'TJ', 'CH', 'BN', 'PD'])}"
            
            # Determinar si es asegurado o beneficiario
            es_asegurado = random.choice([True, False])
            beneficiario_de = None
            
            if not es_asegurado:
                # Buscar un paciente asegurado existente para ser beneficiario
                pacientes_asegurados = Pacientes.objects.filter(asegurado=True)
                if pacientes_asegurados.exists():
                    beneficiario_de = random.choice(pacientes_asegurados)
                else:
                    es_asegurado = True  # Si no hay asegurados, hacer que este sea asegurado
            
            paciente = Pacientes.objects.create(
                nombre=nombre,
                apellido=apellido,
                ci=ci,
                telefono=fake.phone_number()[:15] if random.choice([True, False]) else None,
                email=fake.email() if random.choice([True, False]) else None,
                fecha_nacimiento=fake.date_of_birth(minimum_age=0, maximum_age=90),
                sexo=random.choice(['M', 'F', 'O']),
                residencia=random.choice(['La Paz', 'Santa Cruz', 'Cochabamba', 'Oruro', 'Potosí']),
                direccion=fake.address() if random.choice([True, False]) else None,
                religion=random.choice(['Católica', 'Protestante', 'Agnóstica', 'Otra', None]),
                ocupacion=fake.job() if random.choice([True, False]) else None,
                asegurado=es_asegurado,
                beneficiario_de=beneficiario_de
            )
            
            self.stdout.write(f'Paciente creado: {nombre} {apellido} - CI: {ci}')

    def create_formularios_y_preguntas(self):
        """Crear formularios y preguntas para cada especialidad"""
        especialidades = Especialidad.objects.all()
        
        for especialidad in especialidades:
            # Crear formulario base para la especialidad
            formulario = Formulario.objects.create(
                nombre=f"Formulario de {especialidad.nombre}",
                especialidad=especialidad,
                activo=True
            )
            
            # Preguntas generales para todas las especialidades
            preguntas_generales = [
                ("¿Presenta algún dolor actualmente?", "booleano", True, 1),
                ("Describa el motivo principal de su consulta", "textarea", True, 2),
                ("¿Ha tenido este problema anteriormente?", "booleano", False, 3),
                ("¿Toma algún medicamento regularmente?", "textarea", False, 4),
                ("¿Tiene alergias conocidas?", "textarea", False, 5),
            ]
            
            # Preguntas específicas según la especialidad
            preguntas_especificas = []
            
            if especialidad.nombre == 'Cardiología':
                preguntas_especificas = [
                    ("¿Ha sentido dolor en el pecho?", "booleano", True, 6),
                    ("¿Presenta dificultad para respirar?", "booleano", True, 7),
                    ("¿Ha tenido palpitaciones?", "booleano", False, 8),
                    ("¿Tiene antecedentes familiares de problemas cardíacos?", "booleano", False, 9),
                ]
            elif especialidad.nombre == 'Neurología':
                preguntas_especificas = [
                    ("¿Ha tenido dolores de cabeza frecuentes?", "booleano", True, 6),
                    ("¿Ha experimentado mareos o vértigo?", "booleano", False, 7),
                    ("¿Ha tenido convulsiones?", "booleano", True, 8),
                    ("¿Presenta problemas de memoria?", "booleano", False, 9),
                ]
            elif especialidad.nombre == 'Pediatría':
                preguntas_especificas = [
                    ("¿El niño ha tenido fiebre recientemente?", "booleano", True, 6),
                    ("¿Ha presentado vómitos o diarrea?", "booleano", True, 7),
                    ("¿Está al día con las vacunas?", "booleano", True, 8),
                    ("¿Ha tenido problemas para dormir?", "booleano", False, 9),
                ]
            elif especialidad.nombre == 'Ginecología':
                preguntas_especificas = [
                    ("Fecha de la última menstruación", "fecha", True, 6),
                    ("¿Ha tenido sangrado irregular?", "booleano", True, 7),
                    ("¿Usa algún método anticonceptivo?", "texto", False, 8),
                    ("¿Ha tenido embarazos previos?", "numero", False, 9),
                ]
            elif especialidad.nombre == 'Traumatología':
                preguntas_especificas = [
                    ("¿Cómo ocurrió la lesión?", "textarea", True, 6),
                    ("¿Puede mover la zona afectada?", "booleano", True, 7),
                    ("Del 1 al 10, ¿cuál es el nivel de dolor?", "numero", True, 8),
                    ("¿Ha tenido fracturas anteriores?", "booleano", False, 9),
                ]
            
            # Crear todas las preguntas
            todas_las_preguntas = preguntas_generales + preguntas_especificas
            
            for texto, tipo_dato, obligatorio, orden in todas_las_preguntas:
                Pregunta.objects.create(
                    formulario=formulario,
                    texto=texto,
                    tipo_dato=tipo_dato,
                    obligatorio=obligatorio,
                    orden=orden
                )
            
            self.stdout.write(f'Formulario creado para {especialidad.nombre} con {len(todas_las_preguntas)} preguntas')

    def create_historiales_clinicos(self, count):
        """Crear historiales clínicos con respuestas"""
        pacientes = list(Pacientes.objects.all())
        usuarios_medicos = list(Usuario.objects.filter(rol__nombre__in=['Doctor', 'Residente', 'Jefe de Especialidad']))
        especialidades = list(Especialidad.objects.all())
        formularios = list(Formulario.objects.all())
        
        if not pacientes or not usuarios_medicos or not especialidades:
            self.stdout.write(self.style.WARNING('No hay suficientes datos para crear historiales clínicos'))
            return
        
        motivos_consulta = [
            "Dolor abdominal", "Cefalea intensa", "Fiebre y malestar general",
            "Dolor torácico", "Dificultad respiratoria", "Mareos y náuseas",
            "Dolor de espalda", "Revisión de rutina", "Control post-operatorio",
            "Dolor articular", "Problemas digestivos", "Insomnio",
            "Ansiedad", "Erupción cutánea", "Dolor menstrual"
        ]
        
        diagnosticos = [
            "Gastritis aguda", "Migraña", "Síndrome gripal",
            "Dolor torácico atípico", "Bronquitis aguda", "Vértigo periférico",
            "Lumbalgia mecánica", "Paciente sano", "Evolución satisfactoria",
            "Artritis", "Dispepsia funcional", "Trastorno del sueño",
            "Trastorno de ansiedad", "Dermatitis", "Dismenorrea"
        ]
        
        fuentes = ["Paciente", "Familiar", "Expediente médico", "Referencia médica"]
        confiabilidades = ["Alta", "Media", "Baja", None]
        
        for i in range(count):
            paciente = random.choice(pacientes)
            usuario = random.choice(usuarios_medicos)
            especialidad = random.choice(especialidades)
            
            # Generar signos vitales realistas
            signos_vitales = {
                "presion_arterial_sistolica": random.randint(90, 180),
                "presion_arterial_diastolica": random.randint(60, 110),
                "frecuencia_cardiaca": random.randint(60, 120),
                "frecuencia_respiratoria": random.randint(12, 25),
                "temperatura": round(random.uniform(36.0, 39.5), 1),
                "saturacion_oxigeno": random.randint(92, 100),
                "peso": round(random.uniform(40.0, 120.0), 1),
                "talla": random.randint(140, 190)
            }
            
            # Crear historial clínico
            historial = HistorialClinico.objects.create(
                paciente=paciente,
                usuario=usuario,
                especialidad=especialidad,
                fecha=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone()),
                motivo_consulta=random.choice(motivos_consulta),
                fuente=random.choice(fuentes),
                confiabilidad=random.choice(confiabilidades),
                diagnostico=random.choice(diagnosticos),
                signos_vitales=signos_vitales
            )
            
            # Asignar formulario y crear respuestas
            formularios_especialidad = [f for f in formularios if f.especialidad == especialidad]
            if formularios_especialidad:
                formulario = random.choice(formularios_especialidad)
                historial.formulario = formulario
                historial.save()
                
                # Crear respuestas para las preguntas del formulario
                preguntas = Pregunta.objects.filter(formulario=formulario)
                for pregunta in preguntas:
                    # No todas las preguntas necesitan respuesta (excepto las obligatorias)
                    if pregunta.obligatorio or random.choice([True, False]):
                        valor = self.generar_respuesta_segun_tipo(pregunta.tipo_dato, pregunta.texto)
                        
                        Respuesta.objects.create(
                            pregunta=pregunta,
                            historial_clinico=historial,
                            valor=valor
                        )
            
            self.stdout.write(f'Historial clínico creado para paciente {paciente.nombre} {paciente.apellido}')

    def generar_respuesta_segun_tipo(self, tipo_dato, texto_pregunta):
        """Generar respuesta según el tipo de dato de la pregunta"""
        if tipo_dato == 'booleano':
            return str(random.choice([True, False]))
        elif tipo_dato == 'numero':
            if 'dolor' in texto_pregunta.lower():
                return str(random.randint(1, 10))
            elif 'embarazos' in texto_pregunta.lower():
                return str(random.randint(0, 5))
            else:
                return str(random.randint(1, 100))
        elif tipo_dato == 'fecha':
            fecha = fake.date_between(start_date='-2y', end_date='today')
            return fecha.strftime('%Y-%m-%d')
        elif tipo_dato == 'textarea':
            return fake.text(max_nb_chars=200)
        else:  # texto
            if 'medicamento' in texto_pregunta.lower():
                medicamentos = ['Paracetamol', 'Ibuprofeno', 'Aspirina', 'Ninguno']
                return random.choice(medicamentos)
            elif 'anticonceptivo' in texto_pregunta.lower():
                metodos = ['Pastillas', 'DIU', 'Preservativo', 'Ninguno']
                return random.choice(metodos)
            else:
                return fake.sentence(nb_words=6)