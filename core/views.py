from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Personnel, Team, Sector, Worksite, Assignment, SiteAssessment, BuildingInventory, DamageAssessment, MovableHeritage
from .forms import IntangibleHeritageForm, MovableTrackingForm, PersonnelForm, TeamForm, SectorForm, WorksiteForm, AssignmentForm, SiteAssessmentForm, BuildingInventoryForm, DamageAssessmentForm, MovableHeritageForm
import json
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from .utils import generate_random_password

def home(request):
    """
    Ana Dashboard: Canlı özet, son aktiviteler ve hızlı menü.
    """
    # 1. KARTLAR İÇİN VERİLER
    active_assignments = Assignment.objects.filter(status='ACTIVE').count()
    
    # Kritik Bina Sayısı (Severe + Collapsed)
    critical_buildings = DamageAssessment.objects.filter(
        overall_damage__in=['SEVERE', 'COLLAPSED']
    ).count()
    
    # Toplam Kurtarılan/Kaydedilen Eser
    total_assets = MovableHeritage.objects.count()
    
    # Sahadaki Toplam Personel (Aktif Takımlardaki üye sayısı tahmini veya direkt personel sayısı)
    total_personnel = Personnel.objects.count()

    # 2. SON AKTİVİTELER (Son 5 Hasar Raporu)
    recent_activities = DamageAssessment.objects.select_related(
        'building', 'assignment__team'
    ).order_by('-created_at')[:5]

    # 3. HARİTA İÇİN VERİ (Mevcut fonksiyonu kullanıyoruz)
    map_data = get_operational_map_data()

    context = {
        'active_assignments': active_assignments,
        'critical_buildings': critical_buildings,
        'total_assets': total_assets,
        'total_personnel': total_personnel,
        'recent_activities': recent_activities,
        'map_data': map_data,
    }
    return render(request, 'core/index.html', context)
# 1. Liste Görünümü
class PersonnelListView(ListView):
    model = Personnel
    template_name = 'core/personnel_list.html'
    context_object_name = 'personnel_list'

# 2. Ekleme Görünümü
class PersonnelCreateView(CreateView):
    model = Personnel
    form_class = PersonnelForm
    template_name = 'core/personnel_form.html'
    #success_url = reverse_lazy('personnel_list')
    def form_valid(self, form):
            """
            Form geçerliyse araya gir:
            1. User oluştur
            2. Şifre üret
            3. Personel ile User'ı bağla
            4. Sonra kaydet
            """
            # 1. E-posta kontrolü (Zaten modelde unique=True ama user tablosuna da bakmalıyız)
            email = form.cleaned_data['email']
            if User.objects.filter(username=email).exists():
                form.add_error('email', 'Bu e-posta ile kayıtlı bir sistem kullanıcısı zaten var.')
                return self.form_invalid(form)

            # 2. Şifre Üret ve User Oluştur
            password = generate_random_password()
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # 3. Formdaki instance'a (Personel nesnesine) user'ı ata
            form.instance.user = user
            
            # 4. Standart kaydetme işlemini yap (Many-to-Many dahil)
            self.object = form.save()

            # 5. KRİTİK NOKTA: Şifreyi göstermek için özel bir sayfaya gönder
            # (Bunu yapmak zorundayız çünkü şifreyi bir daha göremeyiz)
            return render(self.request, 'core/personnel_success.html', {
                'personnel': self.object,
                'password': password
            })   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Personnel'
        return context

# 3. Düzenleme Görünümü
class PersonnelUpdateView(UpdateView):
    model = Personnel
    form_class = PersonnelForm
    template_name = 'core/personnel_form.html'
    success_url = reverse_lazy('personnel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Personnel'
        return context

# 4. Silme Görünümü
class PersonnelDeleteView(DeleteView):
    model = Personnel
    template_name = 'core/personnel_confirm_delete.html'
    success_url = reverse_lazy('personnel_list')

class TeamListView(ListView):
    model = Team
    template_name = 'core/team_list.html'
    context_object_name = 'teams'

class TeamCreateView(CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'core/team_form.html'
    success_url = reverse_lazy('team_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Team'
        return context

class TeamUpdateView(UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'core/team_form.html'
    success_url = reverse_lazy('team_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Team'
        return context

class TeamDeleteView(DeleteView):
    model = Team
    template_name = 'core/team_confirm_delete.html'
    success_url = reverse_lazy('team_list')

class SectorListView(ListView):
    model = Sector
    template_name = 'core/sector_list.html'
    context_object_name = 'sectors'

class SectorCreateView(CreateView):
    model = Sector
    form_class = SectorForm
    template_name = 'core/sector_form.html'
    success_url = reverse_lazy('sector_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Sector'
        return context

class SectorUpdateView(UpdateView):
    model = Sector
    form_class = SectorForm
    template_name = 'core/sector_form.html'
    success_url = reverse_lazy('sector_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Sector'
        return context

# --- WORKSITE VIEWS ---
class WorksiteListView(ListView):
    model = Worksite
    template_name = 'core/worksite_list.html'
    context_object_name = 'worksites'

class WorksiteCreateView(CreateView):
    model = Worksite
    form_class = WorksiteForm
    template_name = 'core/worksite_form.html'
    success_url = reverse_lazy('worksite_list')

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Create New Worksite'
            
            sectors_data = []
            for s in Sector.objects.exclude(location_data__isnull=True).exclude(location_data=''):
                try:
                    geom = json.loads(s.location_data)
                    sectors_data.append({
                        'id': s.id,
                        'name': s.name,
                        'color': s.color,
                        'geometry': geom
                    })
                except:
                    pass
            
            # DÜZELTME: json.dumps() kaldırıldı
            context['sectors_json'] = sectors_data 
            return context

class WorksiteUpdateView(UpdateView):
    model = Worksite
    form_class = WorksiteForm
    template_name = 'core/worksite_form.html'
    success_url = reverse_lazy('worksite_list')

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Edit Worksite'
            
            sectors_data = []
            for s in Sector.objects.exclude(location_data__isnull=True).exclude(location_data=''):
                try:
                    geom = json.loads(s.location_data)
                    sectors_data.append({
                        'id': s.id,
                        'name': s.name,
                        'color': s.color,
                        'geometry': geom
                    })
                except:
                    pass
            
            # DÜZELTME: json.dumps() kaldırıldı
            context['sectors_json'] = sectors_data
            return context
def get_operational_map_data():
    """
    Sektörler ve Worksiteları hazırlar. 
    Worksite verisine 'active_teams' ve 'history' bilgisini ekler.
    """
    sectors_data = []
    worksites_data = []

    # 1. Sektörler
    for s in Sector.objects.exclude(location_data__isnull=True).exclude(location_data=''):
        try:
            geom = json.loads(s.location_data)
            sectors_data.append({
                'id': s.id, 'name': s.name, 'color': s.color, 'geometry': geom
            })
        except: pass

    # 2. Worksites ve Operasyon Bilgisi
    for w in Worksite.objects.exclude(location_data__isnull=True).exclude(location_data=''):
        try:
            geom = json.loads(w.location_data)
            
            # Bu sahadaki görevlendirmeleri çek
            assignments = w.assignments.all().order_by('-start_time')
            
            active_teams = []
            history_teams = []
            
            for a in assignments:
                info = {
                    'team': a.team.name,
                    'start': a.start_time.strftime('%Y-%m-%d %H:%M'),
                    'end': a.end_time.strftime('%Y-%m-%d %H:%M') if a.end_time else 'Ongoing',
                    'status': a.status
                }
                if a.status == 'ACTIVE':
                    active_teams.append({
                    'team': a.team.name,
                    'start': a.start_time.strftime('%Y-%m-%d %H:%M'),
                    'assignment_id': a.id,  # <--- YENİ EKLENDİ
                    'status': a.status
                })
                else:
                    history_teams.append(info)

            worksites_data.append({
                'id': w.id,
                'name': w.name,
                'sector_name': w.sector.name if w.sector else "Unassigned",
                'geometry': geom,
                'active_teams': active_teams, # Pop-up için
                'history_teams': history_teams # Pop-up için
            })
        except: pass
            
    return {'sectors': sectors_data, 'worksites': worksites_data}
def get_all_map_data():
    """
    Tüm Sektör ve Worksite verilerini Harita için hazırlar.
    ÖNEMLİ DÜZELTME: json.dumps() KALDIRILDI. Doğrudan Python sözlüğü döndürüyoruz.
    """
    sectors_data = []
    worksites_data = []

    # 1. Sektörleri Hazırla
    for s in Sector.objects.exclude(location_data__isnull=True).exclude(location_data=''):
        try:
            geom = json.loads(s.location_data) # Burada string -> dict dönüşümü yapıyoruz
            sectors_data.append({
                'id': s.id,
                'name': s.name,
                'color': s.color,
                'geometry': geom,
                'description': s.description
            })
        except:
            pass

    # 2. Worksite'ları Hazırla
    for w in Worksite.objects.exclude(location_data__isnull=True).exclude(location_data=''):
        try:
            geom = json.loads(w.location_data)
            worksites_data.append({
                'id': w.id,
                'name': w.name,
                'sector_name': w.sector.name if w.sector else "Unassigned",
                'geometry': geom
            })
        except:
            pass
            
    # HATA BURADAYDI: return json.dumps({...}) yerine
    return {'sectors': sectors_data, 'worksites': worksites_data}

# --- SECTOR VIEWS ---
class SectorListView(ListView):
    model = Sector
    template_name = 'core/sector_list.html'
    context_object_name = 'sectors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Harita için tüm veriyi gönderiyoruz
        context['map_data'] = get_all_map_data()
        return context


# --- WORKSITE VIEWS ---
class WorksiteListView(ListView):
    model = Worksite
    template_name = 'core/worksite_list.html'
    context_object_name = 'worksites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Harita için tüm veriyi gönderiyoruz
        context['map_data'] = get_all_map_data()
        return context
    
# --- ASSIGNMENT VIEWS ---

class AssignmentListView(ListView):
    model = Assignment
    template_name = 'core/assignment_list.html'
    context_object_name = 'assignments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # EKSİK OLAN KISIM BUYDU:
        # Harita verisini (Sektörler, Worksite'lar, Aktif/Pasif Görevler) context'e ekliyoruz.
        context['map_data'] = get_operational_map_data()
        return context

class AssignmentCreateView(CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'core/assignment_form.html'
    success_url = reverse_lazy('assignment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Assign Team to Worksite'
        # Harita verisini gönder
        context['map_data'] = get_operational_map_data()
        return context

class AssignmentUpdateView(UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'core/assignment_form.html'
    success_url = reverse_lazy('assignment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Operation Status'
        context['map_data'] = get_operational_map_data()
        return context
    
# --- FIELD DASHBOARD (ANA KOMUTA MERKEZİ) ---
def field_dashboard(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    worksite = assignment.worksite
    
    site_reports = SiteAssessment.objects.filter(assignment=assignment).prefetch_related(
        'buildings',
        'buildings__damages', # Binalara bağlı hasarlar
        'buildings__assets'   # Binalara bağlı eserler
    )
    
    # (Opsiyonel) Eğer binaları bağımsız listeliyorsan burayı da prefetch yapabilirsin
    buildings = BuildingInventory.objects.filter(assignment=assignment).prefetch_related('damages', 'assets')
    
    context = {
        'assignment': assignment,
        'worksite': worksite,
        'site_reports': site_reports,
        'buildings': buildings,
    }
    return render(request, 'core/field_dashboard.html', context)

# --- 1. SITE FORM EKLEME ---
def add_site_assessment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        form = SiteAssessmentForm(request.POST)
        if form.is_valid():
            site_assessment = form.save(commit=False)
            site_assessment.assignment = assignment
            site_assessment.worksite = assignment.worksite
            site_assessment.editor_name = request.user.username # Giriş yapan kullanıcı
            site_assessment.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = SiteAssessmentForm()
        
    return render(request, 'core/form_entry.html', {
        'form': form, 
        'title': 'Site Assessment (Sec. A-C)',
        'subtitle': assignment.worksite.name
    })

# --- 2. BİNA EKLEME ---
def add_building_inventory(request, assignment_id, site_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    site_assessment = get_object_or_404(SiteAssessment, id=site_id)
    
    if request.method == 'POST':
        form = BuildingInventoryForm(request.POST)
        if form.is_valid():
            building = form.save(commit=False)
            building.assignment = assignment
            building.worksite = assignment.worksite
            building.site_assessment = site_assessment
            building.editor_name = request.user.username
            building.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = BuildingInventoryForm()
        
    return render(request, 'core/form_entry.html', {
        'form': form, 
        'title': 'Building Inventory (Sec. D-H)',
        'subtitle': f"Site: {site_assessment.id}"
    })

def add_damage_assessment(request, assignment_id, building_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    building = get_object_or_404(BuildingInventory, id=building_id)
    
    if request.method == 'POST':
        form = DamageAssessmentForm(request.POST)
        if form.is_valid():
            damage = form.save(commit=False)
            damage.assignment = assignment
            damage.worksite = assignment.worksite
            damage.building = building
            damage.editor_name = request.user.username
            damage.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = DamageAssessmentForm()
        
    return render(request, 'core/form_entry.html', {
        'form': form,
        'title': 'Damage Assessment (Sec. L-M)',
        'subtitle': f"Building: {building.building_name}"
    })

def add_movable_heritage(request, assignment_id, building_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    building = get_object_or_404(BuildingInventory, id=building_id)
    
    if request.method == 'POST':
        form = MovableHeritageForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.assignment = assignment
            asset.worksite = assignment.worksite
            asset.building = building
            asset.editor_name = request.user.username
            asset.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = MovableHeritageForm()
        
    return render(request, 'core/form_entry.html', {
        'form': form,
        'title': 'Movable Heritage (Sec. N-O)',
        'subtitle': f"Location: {building.building_name}"
    })

def reporting_dashboard(request):
    """
    Yönetici Özet Ekranı: İstatistikler, Grafikler ve Acil Durumlar
    """
    # 1. TEMEL KARTLAR (KPIs)
    total_sites = SiteAssessment.objects.count()
    total_buildings = BuildingInventory.objects.count()
    total_assets = MovableHeritage.objects.count()
    
    # Toplam Operasyon Sayısı (Atanan vs Tamamlanan)
    # Not: Assignment modelinde 'status' alanını kullanıyoruz
    total_assignments = Assignment.objects.count()
    completed_assignments = Assignment.objects.filter(status='COMPLETED').count()
    completion_rate = int((completed_assignments / total_assignments) * 100) if total_assignments > 0 else 0

    # 2. HASAR DAĞILIMI (PASTA GRAFİK VERİSİ)
    # Veritabanından hasar türlerine göre gruplayıp sayılarını alıyoruz
    damage_stats = DamageAssessment.objects.values('overall_damage').annotate(total=Count('id'))
    
    # Grafik için etiket ve veri listelerini hazırla
    damage_labels = []
    damage_data = []
    damage_colors = []
    
    color_map = {
        'NONE': '#1cc88a',      # Yeşil
        'LIGHT': '#f6c23e',     # Sarı
        'MODERATE': '#fd7e14',  # Turuncu
        'SEVERE': '#e74a3b',    # Kırmızı
        'COLLAPSED': '#5a5c69'  # Koyu Gri
    }

    for stat in damage_stats:
        # DB'deki 'SEVERE' yazısını listeye ekle
        damage_labels.append(stat['overall_damage']) 
        damage_data.append(stat['total'])
        # Rengi belirle
        damage_colors.append(color_map.get(stat['overall_damage'], '#858796'))

    # 3. KIRMIZI LİSTE (ACİL MÜDAHALE GEREKENLER)
    # Ağır hasarlı (SEVERE) veya Yıkık (COLLAPSED) binaları çek
    red_list_buildings = DamageAssessment.objects.filter(
        overall_damage__in=['SEVERE', 'COLLAPSED']
    ).select_related('building', 'building__site_assessment__worksite').order_by('-created_at')[:10]

    # 4. TAKIM PERFORMANSI
    # Hangi editör kaç rapor girmiş?
    team_performance = SiteAssessment.objects.values('editor_name').annotate(
        total_reports=Count('id')
    ).order_by('-total_reports')

    context = {
        'total_sites': total_sites,
        'total_buildings': total_buildings,
        'total_assets': total_assets,
        'completion_rate': completion_rate,
        
        # Grafik Verileri (JSON olarak template'e gidecek)
        'damage_labels': json.dumps(damage_labels),
        'damage_data': json.dumps(damage_data),
        'damage_colors': json.dumps(damage_colors),
        
        'red_list': red_list_buildings,
        'team_stats': team_performance
    }
    
    return render(request, 'core/reporting_dashboard.html', context)

def download_mission_report(request):
    """
    Sıfırıncı dakikadan bugüne tüm operasyonun detaylı PDF raporunu üretir.
    (xhtml2pdf kullanılarak - Ek kurulum gerektirmez)
    """
    # --- 1. VERİLERİ HAZIRLA (Burada değişiklik yok) ---
    total_sites = SiteAssessment.objects.count()
    total_buildings = BuildingInventory.objects.count()
    
    # Hasar İstatistikleri
    damage_counts = DamageAssessment.objects.values('overall_damage').annotate(count=Count('id'))
    severe_count = 0
    collapsed_count = 0
    for d in damage_counts:
        if d['overall_damage'] == 'SEVERE': severe_count = d['count']
        if d['overall_damage'] == 'COLLAPSED': collapsed_count = d['count']
    
    critical_total = severe_count + collapsed_count

    # Detaylı Saha Verileri
    all_sites = SiteAssessment.objects.prefetch_related(
        'buildings',
        'buildings__damages',
        'buildings__assets',
        'assignment__team'
    ).order_by('created_at')

    # Kırmızı Liste
    red_list = DamageAssessment.objects.filter(
        overall_damage__in=['SEVERE', 'COLLAPSED']
    ).select_related('building', 'building__site_assessment').order_by('overall_damage')

    # Eser Envanteri
    total_assets = MovableHeritage.objects.count()
    assets_list = MovableHeritage.objects.select_related('building').all()

    context = {
        'report_date': timezone.now(),
        'generated_by': request.user.get_full_name() or request.user.username,
        'total_sites': total_sites,
        'total_buildings': total_buildings,
        'critical_total': critical_total,
        'all_sites': all_sites,
        'red_list': red_list,
        'total_assets': total_assets,
        'assets_list': assets_list,
    }

    # --- 2. PDF OLUŞTURMA (DEĞİŞEN KISIM) ---
    
    # HTML'i string olarak al
    html_string = render_to_string('core/report_pdf_template.html', context)
    
    # PDF için bellekte bir dosya (buffer) oluştur
    result = BytesIO()
    
    # xhtml2pdf ile dönüştür (encoding önemli)
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    # Hata kontrolü
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Mission_Report_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    else:
        return HttpResponse("Error Rendering PDF", status=400)
    
def edit_damage_assessment(request, pk):
    damage = get_object_or_404(DamageAssessment, pk=pk)
    assignment = damage.assignment # Dashboard'a dönmek için lazım
    
    if request.method == 'POST':
        form = DamageAssessmentForm(request.POST, instance=damage)
        if form.is_valid():
            form.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = DamageAssessmentForm(instance=damage)
        
    return render(request, 'core/form_entry.html', {
        'form': form,
        'title': 'Edit Damage Report',
        'subtitle': f"Building: {damage.building.building_name}"
    })

def delete_damage_assessment(request, pk):
    damage = get_object_or_404(DamageAssessment, pk=pk)
    assignment_id = damage.assignment.id
    damage.delete()
    return redirect('field_dashboard', assignment_id=assignment_id)

def edit_movable_heritage(request, pk):
    asset = get_object_or_404(MovableHeritage, pk=pk)
    assignment = asset.assignment
    
    if request.method == 'POST':
        form = MovableHeritageForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = MovableHeritageForm(instance=asset)
        
    return render(request, 'core/form_entry.html', {
        'form': form,
        'title': 'Edit Asset',
        'subtitle': f"Object: {asset.object_name}"
    })

def delete_movable_heritage(request, pk):
    asset = get_object_or_404(MovableHeritage, pk=pk)
    assignment_id = asset.assignment.id
    asset.delete()
    return redirect('field_dashboard', assignment_id=assignment_id)

def add_intangible_heritage(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = IntangibleHeritageForm(request.POST)
        if form.is_valid():
            ich = form.save(commit=False)
            ich.assignment = assignment
            ich.worksite = assignment.worksite
            ich.editor_name = request.user.username
            ich.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = IntangibleHeritageForm()
    return render(request, 'core/form_entry.html', {'form': form, 'title': 'Intangible Heritage (Sec. T-Z)'})

def add_intangible_heritage(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = IntangibleHeritageForm(request.POST)
        if form.is_valid():
            ich = form.save(commit=False)
            ich.assignment = assignment
            ich.worksite = assignment.worksite
            ich.editor_name = request.user.username
            ich.save()
            return redirect('field_dashboard', assignment_id=assignment.id)
    else:
        form = IntangibleHeritageForm()
    return render(request, 'core/form_entry.html', {'form': form, 'title': 'Intangible Heritage (Sec. T-Z)'})

def add_movable_tracking(request, asset_id):
    asset = get_object_or_404(MovableHeritage, id=asset_id)
    if request.method == 'POST':
        form = MovableTrackingForm(request.POST)
        if form.is_valid():
            tracking = form.save(commit=False)
            tracking.asset = asset
            tracking.save()
            return redirect('field_dashboard', assignment_id=asset.assignment.id)
    else:
        form = MovableTrackingForm(initial={'team_id': asset.assignment.team.name})
    return render(request, 'core/form_entry.html', {'form': form, 'title': f'Tracking Sheet: {asset.object_name}'})