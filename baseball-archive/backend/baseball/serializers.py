from rest_framework import serializers
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    """선수 정보를 JSON으로 변환하는 Serializer"""
    
    class Meta:
        model = Player
        fields = [
            'id',
            'name',
            'team',
            'position',
            'back_number',
            'batting_average',
            'home_runs',
            'rbis',
            'era',
            'wins',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlayerListSerializer(serializers.ModelSerializer):
    """선수 목록용 간단한 Serializer"""
    
    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'position', 'back_number']

