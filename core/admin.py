from django.contrib import admin
from .models import Personnel, Institution, Country, ExpertiseType, JobTitle, Team # Team'i ekle


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'country', 'email', 'primary_expertise')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('country', 'primary_expertise')

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'count_members', 'created_at')
    search_fields = ('name',)

    # Admin panelinde listede "Üye Sayısı"nı göstermek için özel metod
    def count_members(self, obj):
        return obj.members.count()
    count_members.short_description = 'Member Count'
admin.site.register(Institution)
admin.site.register(Country)
admin.site.register(ExpertiseType)

from .models import Sector, Worksite # Import et

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Worksite)
class WorksiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'created_at')