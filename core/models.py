# core/models.py

from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import User
from django.utils import timezone
import json
# --- YENİ EKLENEN MODEL ---
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Team Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team_leader = models.OneToOneField(
            'Personnel', 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True, 
            related_name='leading_team',
            verbose_name="Team Leader"
        )
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Team"
        verbose_name_plural = "Teams"
# 1. Expertise Types (CSV: EXPERTISE -> DRM, CH, BOTH)
class ExpertiseType(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="e.g., DRM, CH, BOTH")
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.code

# 2. Institutions (CSV: INSTITUTION)
class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
class JobTitle(models.Model):
    title = models.CharField(max_length=200, unique=True)
    
    def __str__(self):
        return self.title
# 3. Countries (CSV: COUNTRY)
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

# 4. Personnel (Ana Tablo)
class Personnel(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    SQ_TYPE_CHOICES = [
        ('BUILDING', 'BUILDING'),
        ('MOVABLE', 'MOVABLE'),
        ('OBSERVER', 'OBSERVER'),
    ]

    # Sistem Giriş Bilgileri (Opsiyonel: Eğer bu personel sisteme login olacaksa)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='personnel_profile')
    team = models.ForeignKey(
            Team, 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True, 
            related_name='members', # team.members.all() ile üyelere ulaşacağız
            verbose_name="Assigned Team"
        )
    # CSV Data Mapping
    sq_number = models.CharField(
            max_length=50, 
            choices=SQ_TYPE_CHOICES, 
            verbose_name="SQ Type", 
            blank=True, 
            null=True
        )
    
    # İlişkisel Alanlar (Dropdown'dan seçilecekler)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name="Country")
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, verbose_name="Institution")
    primary_expertise = models.ForeignKey(ExpertiseType, on_delete=models.SET_NULL, null=True, verbose_name="Main Expertise (DRM/CH)")

    # Metin Alanları
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Male/Female")
    
    job_titles = models.ManyToManyField(
            JobTitle, 
            blank=True, 
            verbose_name="Job Titles",
            help_text="Select multiple or create new ones."
        )
    professional_profile = models.TextField(verbose_name="Professional Profile", blank=True)
    specific_expertise_details = models.TextField(verbose_name="Specific Expertise Details", blank=True)
    
    email = models.EmailField(unique=True, verbose_name="E-mail")
    mobile = models.CharField(max_length=50, verbose_name="Mobile", blank=True)
    
    insurance_code = models.CharField(max_length=100, verbose_name="Code for Insurance", blank=True)
    
    notes = models.TextField(verbose_name="Notes", blank=True)
    private_notes = models.TextField(verbose_name="Private E-mail/Other Notes", blank=True)

    # Metadata (Sistemin tuttuğu kayıt tarihleri)
    is_active = models.BooleanField(default=True, verbose_name="Active Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Personnel"
        verbose_name_plural = "Personnel List"
# --- SECTOR MODELİ (BÖLGE) ---
class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Sector Name")
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default="#3388ff", verbose_name="Map Color") # Örn: #FF0000
    
    # Koordinat verisini JSON string olarak tutacağız (GeoDjango/GDAL zorunluluğunu aşmak için)
    # Format: {"type": "Polygon", "coordinates": [...]}
    location_data = models.TextField(blank=True, null=True, verbose_name="Map Coordinates")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

# --- WORKSITE MODELİ (ÇALIŞMA ALANI) ---
class Worksite(models.Model):   
    STATUS_CHOICES = [
            ('OPEN', 'Open / Active'),
            ('COMPLETED', 'Completed / Closed'),
        ]
    name = models.CharField(max_length=100, verbose_name="Worksite Name")
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True, related_name='worksites')
    description = models.TextField(blank=True, null=True)
    
    # Format: {"type": "Point", "coordinates": [lat, lng]}
    location_data = models.TextField(blank=True, null=True, verbose_name="Map Coordinates")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', verbose_name="Worksite Status")
    completion_date = models.DateField(null=True, blank=True, verbose_name="Completion Date")
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Assignment(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='assignments', verbose_name="Assigned Team")
    worksite = models.ForeignKey(Worksite, on_delete=models.CASCADE, related_name='assignments', verbose_name="Target Worksite")
    
    start_time = models.DateTimeField(default=timezone.now, verbose_name="Start Time")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="End Time (Completion)")
    
    status_choices = [
        ('ACTIVE', 'Active / Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='ACTIVE')
    
    notes = models.TextField(blank=True, null=True, verbose_name="Mission Notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team.name} -> {self.worksite.name}"

    class Meta:
        ordering = ['-start_time']
        verbose_name = "Operation Assignment"
        verbose_name_plural = "Operation Assignments"

class BaseProcultherForm(models.Model):
    """
    Tüm değerlendirme formlarında ortak olan üst bilgiler.
    """
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, related_name="%(class)s_reports")
    worksite = models.ForeignKey('Worksite', on_delete=models.CASCADE)
    
    # Formu dolduran ekip bilgileri
    team_leader = models.CharField(max_length=150, blank=True, verbose_name="Team Leader Name")
    editor_name = models.CharField(max_length=150, verbose_name="Editor Name")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date and Time")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ==========================================
# 2. ALAN DEĞERLENDİRMESİ (FORM 1: SITE)
# ==========================================
class SiteAssessment(BaseProcultherForm):
    """
    Alan (Site) ile ilgili genel tanımlamalar, tehlikeler ve erişim bilgileri.
    """
    # A. Identification
    site_reference_code = models.CharField(max_length=50, blank=True, verbose_name="Site Ref Code")
    region = models.CharField(max_length=100, blank=True, verbose_name="Region")
    province = models.CharField(max_length=100, blank=True, verbose_name="Province")
    municipality = models.CharField(max_length=100, blank=True, verbose_name="Municipality")
    address = models.TextField(blank=True, verbose_name="Address")
    access_notes = models.TextField(blank=True, verbose_name="Access to site")

    # B. Description
    SITE_TYPES = [
        ('ARCH_ELEMENT', 'Architectural element'),
        ('COMPLEX', 'Heritage complex'),
        ('ARCHAEOLOGICAL', 'Archaeological site'),
        ('OTHER', 'Other'),
    ]
    site_type = models.CharField(max_length=50, choices=SITE_TYPES, verbose_name="Type of site")
    number_of_buildings = models.IntegerField(default=1, verbose_name="Number of buildings")
    
    # Detaylar (Tipoloji, Kullanım, Bağlam vb.) - JSON
    description_details = JSONField(default=dict, verbose_name="Description Details")
    
    is_protected = models.CharField(max_length=20, choices=[('YES', 'Protected'), ('NO', 'Not Protected'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', verbose_name="Legal Protection")
    has_intangible_link = models.BooleanField(default=False, verbose_name="Intangible CH Connection")

    # C. Hazard (Tehlikeler) - JSON
    hazard_data = JSONField(default=dict, verbose_name="Hazard Data")

    def __str__(self):
        return f"Site Assessment: {self.worksite.name}"

# ==========================================
# 3. BİNA ENVANTERİ (FORM 2: BUILDING)
# ==========================================
class BuildingInventory(BaseProcultherForm):
    """
    Site içerisindeki binaların fiziksel ve yapısal özellikleri.
    """
    site_assessment = models.ForeignKey(SiteAssessment, on_delete=models.CASCADE, related_name="buildings")

    # D. Identification
    building_code = models.CharField(max_length=50, verbose_name="Building Code")
    building_name = models.CharField(max_length=150, verbose_name="Name of Building")
    address = models.CharField(max_length=255, blank=True, verbose_name="Address")
    
    # E. Description
    description_matrix = JSONField(default=dict, verbose_name="Description Matrix")
    
    surface_area = models.FloatField(null=True, blank=True, verbose_name="Surface Area (m2)")
    avg_height = models.FloatField(null=True, blank=True, verbose_name="Avg Height (m)")
    floors_above = models.IntegerField(default=1, verbose_name="Storeys Overground")
    floors_below = models.IntegerField(default=0, verbose_name="Storeys Underground")
    volume = models.FloatField(null=True, blank=True, verbose_name="Volume (m3)")
    construction_age = models.CharField(max_length=100, blank=True, verbose_name="Age")
    
    # F. Structural Elements - JSON
    structural_elements = JSONField(default=dict, verbose_name="Structural Elements")
    
    # G. Non-Structural & H. Cultural - JSON
    non_structural_elements = JSONField(default=dict, verbose_name="Non-Structural Elements")
    cultural_elements = JSONField(default=dict, verbose_name="Cultural Elements")

    def __str__(self):
        return f"{self.building_name} ({self.building_code})"

# ==========================================
# 4. HASAR TESPİTİ (FORMS 3, 4, 5: DAMAGE)
# ==========================================
class DamageAssessment(BaseProcultherForm):
    """
    Sismik, Yangın ve Sel/Meteorolojik hasar tespitleri.
    """
    building = models.ForeignKey(BuildingInventory, on_delete=models.CASCADE, related_name="damages")
    
    HAZARD_TYPES = [
        ('SEISMIC', 'Seismic'),
        ('FIRE', 'Fire'),
        ('HYDRO', 'Meteorological/Hydro'),
    ]
    hazard_type = models.CharField(max_length=20, choices=HAZARD_TYPES)
    
    # Olay Parametreleri (Yangın tarihi, su seviyesi vb.) - JSON
    event_details = JSONField(default=dict, blank=True, verbose_name="Event Params") 

    # Hasar Matrisleri - JSON
    structural_damage = JSONField(default=dict, verbose_name="Structural Damage Matrix")
    non_structural_damage = JSONField(default=dict, verbose_name="Non-Structural Damage Matrix")

    # Genel Hasar Derecesi
    OVERALL_GRADES = [
        ('NONE', 'No Damage'),
        ('LIGHT', 'Light/Minor'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
        ('COLLAPSED', 'Collapsed'),
    ]
    overall_damage = models.CharField(max_length=20, choices=OVERALL_GRADES, default='NONE')

    # Müdahale Önerileri - JSON
    intervention_needs = JSONField(default=dict, verbose_name="Securing Interventions")

    notes = models.TextField(blank=True, verbose_name="Notes")

    def __str__(self):
        return f"{self.get_hazard_type_display()} - {self.building.building_name}"

# ==========================================
# 5. TAŞINIR KÜLTÜREL MİRAS (FORMS 6, 7, 8)
# ==========================================
class MovableHeritage(BaseProcultherForm):
    """
    Taşınır eserlerin tanımı, kondisyonu ve tahliye ihtiyaçları.
    """
    building = models.ForeignKey(BuildingInventory, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets")
    
    # Tanımlama
    object_name = models.CharField(max_length=200, verbose_name="Object Name")
    category = models.CharField(max_length=100, verbose_name="Type (Painting, Sculpture etc.)")
    quantity = models.CharField(max_length=100, blank=True, verbose_name="Quantity")
    
    # Detaylar - JSON
    description_details = JSONField(default=dict, verbose_name="Materials & Details")
    
    # Hasar ve Kondisyon - JSON
    damage_condition = JSONField(default=dict, verbose_name="Damage Condition")
    
    # İhtiyaçlar - JSON
    evacuation_needs = JSONField(default=dict, verbose_name="Needs & Evacuation")
    
    def __str__(self):
        return f"{self.object_name}"

class MovableTracking(models.Model):
    """
    Eser takip çizelgesi (Transfer geçmişi).
    """
    asset = models.ForeignKey(MovableHeritage, on_delete=models.CASCADE, related_name="movements")
    transfer_date = models.DateTimeField(verbose_name="Date of transfer")
    team_id = models.CharField(max_length=50, verbose_name="Team ID")
    responsible_person = models.CharField(max_length=150, verbose_name="Responsible")
    
    from_location = models.CharField(max_length=255, verbose_name="From (Floor/Room)")
    to_location = models.CharField(max_length=255, verbose_name="To (Storage Site)")
    
    notes = models.TextField(blank=True, verbose_name="Notes")

# ==========================================
# 6. SOMUT OLMAYAN MİRAS (FORMS 9, 10)
# ==========================================
class IntangibleHeritage(BaseProcultherForm):
    """
    Somut olmayan kültürel miras, etki analizi ve yardım ihtiyaçları.
    """
    # Identification
    element_name = models.CharField(max_length=255, verbose_name="Name of Element")
    community_contact = models.CharField(max_length=255, blank=True, verbose_name="Community Contact")
    
    # Description - JSON
    description_data = JSONField(default=dict, verbose_name="Description Data")
    
    # Impact Assessment - JSON
    impact_data = JSONField(default=dict, verbose_name="Impact Data")
    
    # Assistance Needs - JSON
    assistance_needs = JSONField(default=dict, verbose_name="Assistance Needs")

    def __str__(self):
        return self.element_name
    
