from django.urls import path
from .views import (
    PersonnelListView, 
    PersonnelCreateView, 
    PersonnelUpdateView, 
    PersonnelDeleteView, TeamListView, TeamCreateView, TeamUpdateView, TeamDeleteView,
    SectorListView, SectorCreateView, SectorUpdateView,
    WorksiteListView, WorksiteCreateView, WorksiteUpdateView, download_mission_report, home,
    AssignmentListView, AssignmentCreateView, AssignmentUpdateView, reporting_dashboard,
    field_dashboard, add_site_assessment, add_building_inventory, add_damage_assessment, add_movable_heritage,
    edit_damage_assessment, delete_damage_assessment,
    edit_movable_heritage, delete_movable_heritage, add_intangible_heritage, add_movable_tracking
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', home, name='dashboard'),
    # Listeleme
    path('personnel/', PersonnelListView.as_view(), name='personnel_list'),
    
    # Ekleme
    path('personnel/add/', PersonnelCreateView.as_view(), name='personnel_add'),
    
    # Düzenleme
    path('personnel/<int:pk>/edit/', PersonnelUpdateView.as_view(), name='personnel_edit'),
    
    # Silme
    path('personnel/<int:pk>/delete/', PersonnelDeleteView.as_view(), name='personnel_delete'),
    path('teams/', TeamListView.as_view(), name='team_list'),
    path('teams/add/', TeamCreateView.as_view(), name='team_add'),
    path('teams/<int:pk>/edit/', TeamUpdateView.as_view(), name='team_edit'),
    path('teams/<int:pk>/delete/', TeamDeleteView.as_view(), name='team_delete'),
# SECTORS
    path('sectors/', SectorListView.as_view(), name='sector_list'),
    path('sectors/add/', SectorCreateView.as_view(), name='sector_add'),
    path('sectors/<int:pk>/edit/', SectorUpdateView.as_view(), name='sector_edit'),

    # WORKSITES
    path('worksites/', WorksiteListView.as_view(), name='worksite_list'),
    path('worksites/add/', WorksiteCreateView.as_view(), name='worksite_add'),
    path('worksites/<int:pk>/edit/', WorksiteUpdateView.as_view(), name='worksite_edit'),
    path('operations/', AssignmentListView.as_view(), name='assignment_list'),
    path('operations/assign/', AssignmentCreateView.as_view(), name='assignment_add'),
    path('operations/<int:pk>/edit/', AssignmentUpdateView.as_view(), name='assignment_edit'),
    # SAHA OPERASYONLARI
    path('operations/<int:assignment_id>/dashboard/', field_dashboard, name='field_dashboard'),
    
    # FORM GİRİŞLERİ
    path('operations/<int:assignment_id>/site/add/', add_site_assessment, name='add_site_assessment'),
    path('operations/<int:assignment_id>/site/<int:site_id>/building/add/', add_building_inventory, name='add_building_inventory'),
    # HASAR TESPİTİ EKLEME (Damage Assessment)
    path('operations/<int:assignment_id>/building/<int:building_id>/damage/add/', 
         add_damage_assessment, 
         name='add_damage_assessment'),

    # TAŞINIR ESER EKLEME (Movable Heritage)
    path('operations/<int:assignment_id>/building/<int:building_id>/movable/add/', 
         add_movable_heritage, 
         name='add_movable_heritage'),
    path('reporting/', reporting_dashboard, name='reporting_dashboard'),
    path('reporting/pdf/', download_mission_report, name='download_mission_report'),
    # Hasar İşlemleri
    path('damage/<int:pk>/edit/', edit_damage_assessment, name='edit_damage'),
    path('damage/<int:pk>/delete/', delete_damage_assessment, name='delete_damage'),

    # Eser İşlemleri
        path('asset/<int:pk>/edit/', edit_movable_heritage, name='edit_movable_heritage'),
        path('asset/<int:pk>/delete/', delete_movable_heritage, name='delete_movable_heritage'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('operations/<int:assignment_id>/intangible/add/', 
         add_intangible_heritage, 
         name='add_intangible_heritage'),
         
    path('assets/<int:asset_id>/tracking/add/', 
         add_movable_tracking, 
         name='add_movable_tracking'),
]