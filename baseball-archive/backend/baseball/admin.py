from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Django 관리자 페이지에서 선수 관리"""
    
    list_display = ['name', 'team', 'position', 'back_number', 'batting_average', 'era']
    list_filter = ['position', 'team']
    search_fields = ['name', 'team', 'back_number']
    ordering = ['position', 'back_number']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'team', 'position', 'back_number')
        }),
        ('타격 기록', {
            'fields': ('batting_average', 'home_runs', 'rbis'),
            'classes': ('collapse',)
        }),
        ('투수 기록', {
            'fields': ('era', 'wins'),
            'classes': ('collapse',)
        }),
    )
