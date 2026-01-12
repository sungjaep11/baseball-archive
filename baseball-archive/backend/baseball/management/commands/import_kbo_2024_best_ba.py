from django.core.management.base import BaseCommand
from baseball.models import Player
from django.conf import settings
from pathlib import Path
import re

class Command(BaseCommand):
    help = 'kbo_2024_best_ba.sql 파일의 데이터를 데이터베이스에 추가합니다'

    def handle(self, *args, **options):
        self.stdout.write('기존 선수 데이터 삭제 중...\n')
        
        # 기존 데이터 모두 삭제
        deleted_count = Player.objects.all().delete()[0]
        self.stdout.write(self.style.WARNING(f'기존 데이터 {deleted_count}개 삭제됨\n'))
        
        self.stdout.write('KBO 2024 최고 타율 선수 데이터 추가 중...\n')
        
        # SQL 파일 경로 (backend 디렉토리 기준)
        base_dir = Path(settings.BASE_DIR)
        sql_file_path = base_dir / 'kbo_2024_best_ba.sql'
        
        # 포지션 매핑 (SQL -> Django 모델)
        position_mapping = {
            '1B': 'first',
            '2B': 'second',
            '3B': 'third',
            'C': 'catcher',
            'SS': 'shortstop',
            'LF': 'left',
            'CF': 'center',
            'RF': 'right',
        }
        
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # INSERT 문에서 데이터 추출
            insert_pattern = r"INSERT INTO kbo_2024_best_ba.*?VALUES\s*\((\d+),\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*([\d.]+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)"
            matches = re.findall(insert_pattern, sql_content)
            
            created_count = 0
            error_count = 0
            
            for match in matches:
                try:
                    season, team, position_sql, name, batting_avg, rbi, hr, sb, pa = match
                    
                    # 포지션 매핑
                    position = position_mapping.get(position_sql)
                    if not position:
                        self.stdout.write(self.style.WARNING(f'알 수 없는 포지션: {position_sql} (선수: {name})'))
                        error_count += 1
                        continue
                    
                    # back_number는 SQL에 없으므로 임시로 0 사용
                    # 기존 데이터를 모두 삭제했으므로 새로 생성만 함
                    player = Player.objects.create(
                        name=name,
                        team=team,
                        position=position,
                        back_number=0,  # SQL에 등번호 정보가 없음
                        batting_average=float(batting_avg),
                        rbis=int(rbi),
                        home_runs=int(hr),
                        stolen_bases=int(sb),
                    )
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ {name} ({team}, {position_sql}) 추가됨'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'오류 발생: {name if "name" in locals() else "알 수 없음"} - {str(e)}'))
                    error_count += 1
            
            self.stdout.write('\n')
            self.stdout.write(self.style.SUCCESS(f'완료! 총 {len(matches)}명 처리됨'))
            self.stdout.write(self.style.SUCCESS(f'새로 추가: {created_count}명'))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f'오류 발생: {error_count}명'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'파일을 찾을 수 없습니다: {sql_file_path}'))
            self.stdout.write(self.style.ERROR('backend 디렉토리에서 실행해주세요.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'오류 발생: {str(e)}'))
