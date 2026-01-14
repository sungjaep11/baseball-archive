from django.core.management.base import BaseCommand
from baseball.models import Player

class Command(BaseCommand):
    help = '2024 KBO 샘플 선수 데이터를 데이터베이스에 추가합니다'

    def handle(self, *args, **options):
        self.stdout.write('샘플 선수 데이터 추가 중...\n')
        
        # 2024 KBO 주요 선수 데이터
        sample_players = [
            # 투수
            {'name': '양현종', 'team': 'KIA 타이거즈', 'position': 'pitcher', 'back_number': 54, 'era': 2.45, 'wins': 15},
            {'name': '고영표', 'team': 'KT 위즈', 'position': 'pitcher', 'back_number': 32, 'era': 3.12, 'wins': 12},
            {'name': '임찬규', 'team': 'LG 트윈스', 'position': 'pitcher', 'back_number': 27, 'era': 2.88, 'wins': 14},
            {'name': '원태인', 'team': '삼성 라이온즈', 'position': 'pitcher', 'back_number': 13, 'era': 3.45, 'wins': 10},
            {'name': '박영현', 'team': 'KT 위즈', 'position': 'pitcher', 'back_number': 41, 'era': 3.67, 'wins': 9},
            
            # 포수
            {'name': '양의지', 'team': '두산 베어스', 'position': 'catcher', 'back_number': 25, 'batting_average': 0.298, 'home_runs': 18, 'rbis': 72},
            {'name': '강민호', 'team': '롯데 자이언츠', 'position': 'catcher', 'back_number': 27, 'batting_average': 0.285, 'home_runs': 12, 'rbis': 58},
            {'name': '유강남', 'team': 'NC 다이노스', 'position': 'catcher', 'back_number': 32, 'batting_average': 0.272, 'home_runs': 8, 'rbis': 45},
            {'name': '박동원', 'team': 'LG 트윈스', 'position': 'catcher', 'back_number': 27, 'batting_average': 0.266, 'home_runs': 10, 'rbis': 52},
            {'name': '이지영', 'team': '키움 히어로즈', 'position': 'catcher', 'back_number': 22, 'batting_average': 0.258, 'home_runs': 6, 'rbis': 38},
            
            # 1루수
            {'name': '최형우', 'team': 'KIA 타이거즈', 'position': 'first', 'back_number': 34, 'batting_average': 0.315, 'home_runs': 28, 'rbis': 95},
            {'name': '박병호', 'team': 'KT 위즈', 'position': 'first', 'back_number': 52, 'batting_average': 0.295, 'home_runs': 32, 'rbis': 102},
            {'name': '오재일', 'team': '두산 베어스', 'position': 'first', 'back_number': 5, 'batting_average': 0.288, 'home_runs': 15, 'rbis': 68},
            {'name': '나성범', 'team': 'NC 다이노스', 'position': 'first', 'back_number': 9, 'batting_average': 0.302, 'home_runs': 22, 'rbis': 85},
            {'name': '김재환', 'team': '두산 베어스', 'position': 'first', 'back_number': 27, 'batting_average': 0.278, 'home_runs': 18, 'rbis': 72},
            
            # 2루수
            {'name': '김도영', 'team': 'KIA 타이거즈', 'position': 'second', 'back_number': 5, 'batting_average': 0.347, 'home_runs': 38, 'rbis': 109},
            {'name': '김혜성', 'team': '키움 히어로즈', 'position': 'second', 'back_number': 3, 'batting_average': 0.318, 'home_runs': 11, 'rbis': 52},
            {'name': '박민우', 'team': 'NC 다이노스', 'position': 'second', 'back_number': 23, 'batting_average': 0.305, 'home_runs': 8, 'rbis': 48},
            {'name': '오지환', 'team': 'LG 트윈스', 'position': 'second', 'back_number': 24, 'batting_average': 0.292, 'home_runs': 14, 'rbis': 62},
            {'name': '이정후', 'team': '키움 히어로즈', 'position': 'second', 'back_number': 50, 'batting_average': 0.349, 'home_runs': 23, 'rbis': 113},
            
            # 유격수
            {'name': '김하성', 'team': '키움 히어로즈', 'position': 'shortstop', 'back_number': 7, 'batting_average': 0.306, 'home_runs': 15, 'rbis': 58},
            {'name': '박건우', 'team': '두산 베어스', 'position': 'shortstop', 'back_number': 7, 'batting_average': 0.298, 'home_runs': 12, 'rbis': 55},
            {'name': '김선빈', 'team': 'KIA 타이거즈', 'position': 'shortstop', 'back_number': 6, 'batting_average': 0.285, 'home_runs': 10, 'rbis': 52},
            {'name': '정성훈', 'team': '한화 이글스', 'position': 'shortstop', 'back_number': 8, 'batting_average': 0.272, 'home_runs': 8, 'rbis': 45},
            {'name': '손아섭', 'team': 'LG 트윈스', 'position': 'shortstop', 'back_number': 5, 'batting_average': 0.268, 'home_runs': 6, 'rbis': 38},
            
            # 3루수
            {'name': '강백호', 'team': 'KT 위즈', 'position': 'third', 'back_number': 50, 'batting_average': 0.330, 'home_runs': 36, 'rbis': 117},
            {'name': '최정', 'team': 'SK 와이번스', 'position': 'third', 'back_number': 14, 'batting_average': 0.308, 'home_runs': 40, 'rbis': 121},
            {'name': '김강민', 'team': '삼성 라이온즈', 'position': 'third', 'back_number': 52, 'batting_average': 0.295, 'home_runs': 22, 'rbis': 78},
            {'name': '노시환', 'team': '한화 이글스', 'position': 'third', 'back_number': 35, 'batting_average': 0.282, 'home_runs': 25, 'rbis': 88},
            {'name': '김민성', 'team': 'LG 트윈스', 'position': 'third', 'back_number': 28, 'batting_average': 0.275, 'home_runs': 18, 'rbis': 65},
            
            # 좌익수
            {'name': '이정훈', 'team': 'KIA 타이거즈', 'position': 'left', 'back_number': 10, 'batting_average': 0.325, 'home_runs': 15, 'rbis': 68},
            {'name': '오재원', 'team': '두산 베어스', 'position': 'left', 'back_number': 3, 'batting_average': 0.295, 'home_runs': 12, 'rbis': 58},
            {'name': '박민우', 'team': 'KT 위즈', 'position': 'left', 'back_number': 8, 'batting_average': 0.288, 'home_runs': 10, 'rbis': 52},
            {'name': '이대호', 'team': '롯데 자이언츠', 'position': 'left', 'back_number': 10, 'batting_average': 0.278, 'home_runs': 18, 'rbis': 72},
            {'name': '박한이', 'team': 'SK 와이번스', 'position': 'left', 'back_number': 51, 'batting_average': 0.272, 'home_runs': 8, 'rbis': 45},
            
            # 중견수
            {'name': '이용규', 'team': 'KIA 타이거즈', 'position': 'center', 'back_number': 7, 'batting_average': 0.312, 'home_runs': 18, 'rbis': 72},
            {'name': '김헌곤', 'team': 'LG 트윈스', 'position': 'center', 'back_number': 4, 'batting_average': 0.305, 'home_runs': 14, 'rbis': 62},
            {'name': '박민', 'team': '한화 이글스', 'position': 'center', 'back_number': 1, 'batting_average': 0.298, 'home_runs': 12, 'rbis': 58},
            {'name': '이대형', 'team': 'KT 위즈', 'position': 'center', 'back_number': 15, 'batting_average': 0.285, 'home_runs': 10, 'rbis': 52},
            {'name': '권희동', 'team': 'NC 다이노스', 'position': 'center', 'back_number': 6, 'batting_average': 0.278, 'home_runs': 8, 'rbis': 45},
            
            # 우익수
            {'name': '소크라테스', 'team': 'NC 다이노스', 'position': 'right', 'back_number': 30, 'batting_average': 0.338, 'home_runs': 31, 'rbis': 98},
            {'name': '전준우', 'team': 'LG 트윈스', 'position': 'right', 'back_number': 51, 'batting_average': 0.318, 'home_runs': 22, 'rbis': 85},
            {'name': '로하스', 'team': 'KT 위즈', 'position': 'right', 'back_number': 23, 'batting_average': 0.305, 'home_runs': 28, 'rbis': 92},
            {'name': '황성빈', 'team': '두산 베어스', 'position': 'right', 'back_number': 31, 'batting_average': 0.295, 'home_runs': 18, 'rbis': 72},
            {'name': '이성우', 'team': '한화 이글스', 'position': 'right', 'back_number': 44, 'batting_average': 0.288, 'home_runs': 15, 'rbis': 65},
        ]
        
        created_count = 0
        updated_count = 0
        
        for player_data in sample_players:
            player, created = Player.objects.update_or_create(
                name=player_data['name'],
                back_number=player_data['back_number'],
                defaults={
                    'team': player_data['team'],
                    'position': player_data['position'],
                    'batting_average': player_data.get('batting_average'),
                    'home_runs': player_data.get('home_runs'),
                    'rbis': player_data.get('rbis'),
                    'era': player_data.get('era'),
                    'wins': player_data.get('wins'),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ {player.name} ({player.get_position_display()}) 추가됨'))
            else:
                updated_count += 1
                self.stdout.write(f'- {player.name} ({player.get_position_display()}) 업데이트됨')
        
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(f'완료! 총 {len(sample_players)}명 처리됨'))
        self.stdout.write(self.style.SUCCESS(f'새로 추가: {created_count}명, 업데이트: {updated_count}명'))

