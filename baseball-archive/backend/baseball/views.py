from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerSerializer, PlayerListSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    """
    선수 관련 API ViewSet
    
    - GET /api/players/ : 모든 선수 목록 조회
    - GET /api/players/{id}/ : 특정 선수 조회
    - GET /api/players/by_position/?position=pitcher : 포지션별 선수 조회
    - POST /api/players/ : 새 선수 생성
    - PUT/PATCH /api/players/{id}/ : 선수 정보 수정
    - DELETE /api/players/{id}/ : 선수 삭제
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    
    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == 'list':
            return PlayerListSerializer
        return PlayerSerializer
    
    @action(detail=False, methods=['get'])
    def by_position(self, request):
        """
        포지션별 선수 목록 조회
        사용 예: GET /api/players/by_position/?position=pitcher
        """
        position = request.query_params.get('position', None)
        
        if position is None:
            return Response(
                {'error': 'position 파라미터가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        players = self.queryset.filter(position=position)
        serializer = PlayerListSerializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_by_position(self, request):
        """
        모든 포지션별로 그룹화된 선수 목록 조회
        사용 예: GET /api/players/all_by_position/
        """
        positions = ['pitcher', 'catcher', 'first', 'second', 'shortstop', 
                    'third', 'left', 'center', 'right']
        
        result = {}
        for pos in positions:
            players = self.queryset.filter(position=pos)
            serializer = PlayerListSerializer(players, many=True)
            result[pos] = serializer.data
        
        return Response(result)
