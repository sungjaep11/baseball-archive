from django.db import models

class Player(models.Model):
    """야구 선수 모델"""
    
    POSITION_CHOICES = [
        ('pitcher', '투수'),
        ('catcher', '포수'),
        ('first', '1루수'),
        ('second', '2루수'),
        ('shortstop', '유격수'),
        ('third', '3루수'),
        ('left', '좌익수'),
        ('center', '중견수'),
        ('right', '우익수'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='선수명')
    team = models.CharField(max_length=50, verbose_name='팀명')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name='포지션')
    back_number = models.IntegerField(verbose_name='등번호')
    
    # 추가 정보 (나중에 확장 가능)
    batting_average = models.FloatField(null=True, blank=True, verbose_name='타율')
    home_runs = models.IntegerField(null=True, blank=True, verbose_name='홈런')
    rbis = models.IntegerField(null=True, blank=True, verbose_name='타점')
    era = models.FloatField(null=True, blank=True, verbose_name='평균자책점')
    wins = models.IntegerField(null=True, blank=True, verbose_name='승')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        db_table = 'players'
        verbose_name = '선수'
        verbose_name_plural = '선수들'
        ordering = ['position', 'back_number']
    
    def __str__(self):
        return f"{self.name} ({self.get_position_display()}) #{self.back_number}"
