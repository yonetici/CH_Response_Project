from django import forms
from .models import Personnel, MovableTracking, Institution, JobTitle, Team,Sector, Worksite, Assignment,SiteAssessment, BuildingInventory, DamageAssessment, MovableHeritage, IntangibleHeritage
class BootstrapFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Mevcut sınıfları al
            attrs = field.widget.attrs
            existing_class = attrs.get('class', '')
            
            # Checkbox ise farklı stil, değilse standart input stili
            if isinstance(field.widget, forms.CheckboxInput):
                attrs['class'] = f"{existing_class} form-check-input".strip()
            elif isinstance(field.widget, forms.Select):
                attrs['class'] = f"{existing_class} form-select".strip()
            else:
                attrs['class'] = f"{existing_class} form-control".strip()
# --- ÖZEL ALAN SINIFI ---
# "Bu değer listede yok" hatasını engelleyen sınıf
class TagMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        return True # Validation bypass (Her değeri kabul et)

class PersonnelForm(forms.ModelForm):
    # Institution: Tekli Seçim
    institution = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select select2-institution'})
    )
    
    # Job Titles: Çoklu Seçim
    job_titles = TagMultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2-job-title'})
    )

    class Meta:
        model = Personnel
        fields = [
            'first_name', 'last_name', 'sq_number', 'gender', 'country',
            'institution', 'job_titles', 
            'professional_profile', 'primary_expertise', 'specific_expertise_details',
            'email', 'mobile', 'insurance_code', 'notes', 'private_notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'private_notes': forms.Textarea(attrs={'rows': 3}),
            'specific_expertise_details': forms.Textarea(attrs={'rows': 3}),
            'professional_profile': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Stil Atamaları (Bootstrap Class'ları)
        for field in self.fields:
            if field not in ['institution', 'job_titles']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        select_fields = ['gender', 'country', 'primary_expertise', 'sq_number']
        for field_name in select_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': 'form-select'})

        # --- INSTITUTION AYARLARI ---
        inst_choices = [(str(i.id), i.name) for i in Institution.objects.all()]
        self.fields['institution'].widget.choices = inst_choices
        
        if self.instance.pk and self.instance.institution:
            self.fields['institution'].initial = str(self.instance.institution.id)

        # --- JOB TITLES AYARLARI ---
        # 1. Seçenekleri Doldur
        title_choices = [(str(j.id), j.title) for j in JobTitle.objects.all()]
        self.fields['job_titles'].choices = title_choices
        self.fields['job_titles'].widget.choices = title_choices # Widget'a da veriyoruz

        # 2. Mevcut Verileri Yükle (Edit Modu)
        if self.instance.pk:
            existing_ids = [str(j.id) for j in self.instance.job_titles.all()]
            self.fields['job_titles'].initial = existing_ids
            self.initial['job_titles'] = existing_ids

    def clean_institution(self):
        """Gelen veriyi (ID veya İsim) Institution Nesnesine çevirir."""
        data = self.cleaned_data.get('institution')
        if not data:
            return None
        
        if data.isdigit() and Institution.objects.filter(id=int(data)).exists():
            return Institution.objects.get(id=int(data))
        else:
            obj, _ = Institution.objects.get_or_create(name=data.strip())
            return obj

    def clean_job_titles(self):
        """Gelen listeyi (ID'ler veya İsimler) JobTitle Nesneleri listesine çevirir."""
        data = self.cleaned_data.get('job_titles', [])
        final_list = []
        
        for item in data:
            if item.isdigit() and JobTitle.objects.filter(id=int(item)).exists():
                final_list.append(JobTitle.objects.get(id=int(item)))
            else:
                clean_title = item.strip()
                if clean_title:
                    obj, _ = JobTitle.objects.get_or_create(title=clean_title)
                    final_list.append(obj)
        return final_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if 'job_titles' in self.cleaned_data:
                instance.job_titles.set(self.cleaned_data['job_titles'])     
        return instance

# --- TEAM FORM ---
class TeamForm(forms.ModelForm):
    # Sanal Alan: Takım Üyelerini Seçmek İçin
    members = forms.ModelMultipleChoiceField(
        queryset=Personnel.objects.none(), # Başlangıçta boş, __init__ içinde mantıkla dolacak
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2-members'}),
        label="Select Team Members"
    )

    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. TEMEL KURAL: Sadece takımı olmayan personelleri al
        available_personnel = Personnel.objects.filter(team__isnull=True)

        # 2. DÜZENLEME (EDIT) MODU:
        if self.instance.pk:
            # Mevcut takımın üyelerini de al (Yoksa listede görünmez ve silinirler)
            current_members = Personnel.objects.filter(team=self.instance)
            
            # İki grubu birleştir: (Boştakiler) + (Bu Takımdakiler)
            self.fields['members'].queryset = (available_personnel | current_members).distinct()
            
            # Form açıldığında mevcut üyeler seçili gelsin
            self.fields['members'].initial = self.instance.members.all()
        else:
            # YENİ KAYIT (CREATE) MODU:
            # Sadece boşta olanları göster
            self.fields['members'].queryset = available_personnel

    def save(self, commit=True):
        # 1. Önce Takımı Kaydet
        team = super().save(commit=commit)
        
        # 2. Üyeleri Güncelle
        if commit:
            # Formdan seçilen personelleri al
            selected_members = self.cleaned_data.get('members', [])
            
            # A) LİSTEDEN ÇIKARILANLAR:
            # Bu takıma ait olup, yeni listede olmayanları boşa çıkar (Team=None)
            team.members.exclude(id__in=[p.id for p in selected_members]).update(team=None)
            
            # B) LİSTEYE EKLENENLER:
            # Seçilen personelleri bu takıma ata
            for person in selected_members:
                person.team = team
                person.save()
                
        return team
    
class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['name', 'description', 'color', 'location_data']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'location_data': forms.HiddenInput(), # Gizli alan, JS dolduracak
        }

class WorksiteForm(forms.ModelForm):
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select select2-sector'}), # Select2 kullanacağız
        empty_label="Select Sector (or pick on map)"
    )

    class Meta:
            model = Worksite
            fields = ['name', 'sector', 'description', 'location_data', 'status', 'completion_date'] # Yeni alanları ekledik
            widgets = {
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'location_data': forms.HiddenInput(),
                
                # YENİ WIDGET'LAR
                'status': forms.Select(attrs={'class': 'form-select'}),
                'completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            }

class AssignmentForm(forms.ModelForm):
    # Team ve Worksite için Select2 (Aramalı seçim)
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2-team'})
    )
    worksite = forms.ModelChoiceField(
        queryset=Worksite.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2-worksite'})
    )

    class Meta:
        model = Assignment
        fields = ['team', 'worksite', 'start_time', 'end_time', 'status', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- 1. SITE ASSESSMENT FORM (Mixin'i ekledik) ---
class SiteAssessmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SiteAssessment
        fields = [
            'site_reference_code', 'region', 'province', 'municipality', 
            'address', 'access_notes', 'site_type', 'number_of_buildings', 
            'is_protected', 'has_intangible_link'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Full address...'}),
            'access_notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Road conditions, entry points...'}),
        }

# --- 2. BUILDING INVENTORY FORM ---
class BuildingInventoryForm(BootstrapFormMixin, forms.ModelForm):
    # PDF E.1, E.2, E.3 Choice alanları
    PLAN_LAYOUT_CHOICES = [('REGULAR', 'Regular'), ('ELONGATED', 'Elongated'), ('COURTYARD', 'Courtyard'), ('IRREGULAR', 'Irregular')]
    POSITION_CHOICES = [('ISOLATED', 'Isolated'), ('INNER', 'Inner'), ('BORDER', 'Border'), ('CORNER', 'Corner')]
    
    plan_layout = forms.ChoiceField(choices=PLAN_LAYOUT_CHOICES, required=False)
    position = forms.ChoiceField(choices=POSITION_CHOICES, required=False)

    class Meta:
        model = BuildingInventory
        fields = [
            'building_code', 'building_name', 'address', 'plan_layout', 'position',
            'surface_area', 'avg_height', 'floors_above', 'floors_below', 'volume'
        ]
# --- 3. DAMAGE ASSESSMENT FORM ---
class DamageAssessmentForm(BootstrapFormMixin, forms.ModelForm):
    # Ekstra parametreler (View'da event_details JSON'a map edilecek)
    water_level_cm = forms.IntegerField(required=False, label="Max Water Level (cm)")
    water_type = forms.ChoiceField(choices=[('CLEAN','Clean'),('MUDDY','Muddy'),('SEA','Sea Water')], required=False)
    fire_origin = forms.ChoiceField(choices=[('INTERNAL','Internal'),('EXTERNAL','External')], required=False)

    class Meta:
        model = DamageAssessment
        fields = ['hazard_type', 'overall_damage', 'water_level_cm', 'water_type', 'fire_origin', 'notes']
# --- 4. MOVABLE HERITAGE FORM ---
class MovableHeritageForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MovableHeritage
        fields = ['object_name', 'category', 'quantity']
        widgets = {
            'object_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }

class IntangibleHeritageForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = IntangibleHeritage
        fields = ['element_name', 'community_contact']
        # PDF Bölüm 9 & 10 (Sayfa 22-26) detayları için JSON alanlarını 
        # View tarafında veya formda ayrıca handle edeceğiz.
        widgets = {
            'element_name': forms.TextInput(attrs={'placeholder': 'Name of the ritual, craft or tradition...'}),
        }

class MovableTrackingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MovableTracking
        fields = ['transfer_date', 'team_id', 'responsible_person', 'from_location', 'to_location', 'notes']
        widgets = {
            'transfer_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }