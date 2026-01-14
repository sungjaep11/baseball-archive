import boto3
import pymysql
import os
import sys
import mimetypes
import re

# 상위 디렉토리 경로 추가 (config 모듈 접근을 위해)
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# db_config는 backend/config 폴더에 있음 (gitignore에 포함되어 커밋되지 않음)
from config.db_config import DB_CONFIG

# ==========================================
# 1. AWS S3 설정
# ==========================================
# AWS 자격 증명은 config/aws_config.py에서 가져옵니다
try:
    from config.aws_config import AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME, REGION
except ImportError:
    # aws_config.py가 없으면 환경 변수 또는 placeholder 사용
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID', 'your-aws-access-key-id')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'your-aws-secret-access-key')
    BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'your-bucket-name')
    REGION = os.getenv('AWS_REGION', 'ap-northeast-2')

IMAGE_FOLDER = 'player_images'

def upload_s3_and_update_db(clear_existing=False):
    """
    player_images 폴더의 이미지를 S3에 업로드하고 photo_data 테이블에 저장합니다.
    
    Args:
        clear_existing (bool): True이면 기존 photo_data 테이블의 모든 데이터를 삭제하고 새로 시작
    """
    # 1. S3 연결
    s3 = boto3.client('s3', 
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY,
                      region_name=REGION)
    print("✅ S3 연결 성공!")

    # 2. DB 연결
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 3. 기존 데이터 삭제 옵션
    if clear_existing:
        try:
            cursor.execute("TRUNCATE TABLE photo_data")
            conn.commit()
            print("🗑️  기존 photo_data 테이블 데이터를 모두 삭제했습니다.")
        except Exception as e:
            print(f"⚠️ 테이블 삭제 중 오류 (테이블이 없을 수 있음): {e}")
            # 테이블이 없으면 생성
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS photo_data (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        player_id VARCHAR(20) NULL,
                        player_name VARCHAR(100) NOT NULL,
                        image_1 VARCHAR(500) NULL,
                        image_2 VARCHAR(500) NULL,
                        image_3 VARCHAR(500) NULL,
                        profile_img VARCHAR(500) NULL,
                        INDEX idx_player_name (player_name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                conn.commit()
                print("✅ photo_data 테이블을 생성했습니다.")
            except Exception as e2:
                print(f"⚠️ 테이블 생성 중 오류: {e2}")

    files = os.listdir(IMAGE_FOLDER)
    print(f"🚀 {len(files)}개의 이미지를 S3로 전송합니다...")

    try:
        for filename in files:
            if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                continue

            # 파일 경로
            file_path = os.path.join(IMAGE_FOLDER, filename)
            
            # 선수 이름 추출 (예: 류현진_1.jpg -> 류현진, 류현진_profile.jpg -> 류현진)
            # 파일명 형식: {선수명}_1.jpg, {선수명}_2.jpg, {선수명}_3.jpg, {선수명}_profile.jpg
            name_without_ext = os.path.splitext(filename)[0]
            match = re.match(r'^(.+?)_(1|2|3|profile)$', name_without_ext)
            if match:
                player_name = match.group(1)
                image_type = match.group(2)
            else:
                # 형식이 맞지 않으면 건너뜀
                print(f"⚠️ 건너뜀: 파일명 형식 오류 ({filename})")
                continue

            # S3에 저장될 파일 이름 (중복 방지를 위해 폴더링 추천)
            # 예: players/류현진_1.jpg
            s3_file_name = f"players/{filename}"

            try:
                # (1) S3 업로드
                # ContentType을 설정해야 브라우저에서 바로 보입니다.
                content_type = mimetypes.guess_type(file_path)[0] or 'image/jpeg'
                
                s3.upload_file(
                    file_path, 
                    BUCKET_NAME, 
                    s3_file_name,
                    ExtraArgs={'ContentType': content_type}
                )

                # (2) URL 생성
                image_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{s3_file_name}"

                # (3) 이미지 타입별 컬럼 매핑 (기존 컬럼 사용)
                column_map = {
                    '1': 'image_1',
                    '2': 'image_2',
                    '3': 'image_3',
                    'profile': 'profile_img'
                }
                
                target_column = column_map.get(image_type)
                if not target_column:
                    print(f"⚠️ 알 수 없는 이미지 타입: {image_type}")
                    continue
                
                # (4) 컬럼 타입이 LONGBLOB이면 VARCHAR로 변경 (URL 저장을 위해)
                try:
                    # 컬럼 타입 확인 및 변경
                    cursor.execute("""
                        SELECT DATA_TYPE 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = %s 
                        AND TABLE_NAME = 'photo_data' 
                        AND COLUMN_NAME = %s
                    """, (DB_CONFIG['db'], target_column))
                    
                    result = cursor.fetchone()
                    if result and result.get('DATA_TYPE') in ('longblob', 'blob', 'mediumblob'):
                        # LONGBLOB → VARCHAR(500)로 변경
                        cursor.execute("ALTER TABLE photo_data MODIFY COLUMN {} VARCHAR(500)".format(target_column))
                        conn.commit()
                        print(f"✅ {target_column} 컬럼 타입을 VARCHAR(500)으로 변경 완료")
                except Exception as e:
                    # 컬럼이 없거나 이미 VARCHAR 타입이면 무시
                    print(f"  ℹ️ {target_column} 컬럼 타입 확인/변경: {e}")

                # (5) kbo_hitters_top150 또는 kbo_pitchers_top150에서 player_id 조회
                player_id = None
                try:
                    # 타자 테이블에서 먼저 조회
                    cursor.execute("""
                        SELECT player_id FROM kbo_hitters_top150 
                        WHERE 선수명 = %s 
                        LIMIT 1
                    """, (player_name,))
                    result = cursor.fetchone()
                    if result and result.get('player_id'):
                        player_id = result.get('player_id')
                    else:
                        # 타자 테이블에 없으면 투수 테이블에서 조회
                        cursor.execute("""
                            SELECT player_id FROM kbo_pitchers_top150 
                            WHERE 선수명 = %s 
                            LIMIT 1
                        """, (player_name,))
                        result = cursor.fetchone()
                        if result and result.get('player_id'):
                            player_id = result.get('player_id')
                except Exception as e:
                    print(f"  ⚠️ player_id 조회 중 오류: {e}")

                # (6) DB 업데이트 또는 삽입 (기존 컬럼에 URL 저장)
                # 먼저 해당 선수가 있는지 확인
                cursor.execute("SELECT id, player_id FROM photo_data WHERE player_name = %s", (player_name,))
                existing_row = cursor.fetchone()
                
                if existing_row:
                    # 기존 행이 있으면 UPDATE
                    # player_id가 없고 조회한 player_id가 있으면 함께 업데이트
                    if not existing_row.get('player_id') and player_id:
                        sql = f"UPDATE photo_data SET {target_column} = %s, player_id = %s WHERE player_name = %s"
                        cursor.execute(sql, (image_url, player_id, player_name))
                        print(f"🔄 업데이트: {player_name} ({image_type}) [player_id: {player_id}] -> {image_url}")
                    else:
                        sql = f"UPDATE photo_data SET {target_column} = %s WHERE player_name = %s"
                        cursor.execute(sql, (image_url, player_name))
                        print(f"🔄 업데이트: {player_name} ({image_type}) -> {image_url}")
                    conn.commit()
                else:
                    # 기존 행이 없으면 INSERT (player_id도 함께 저장)
                    if player_id:
                        sql = f"INSERT INTO photo_data (player_name, player_id, {target_column}) VALUES (%s, %s, %s)"
                        cursor.execute(sql, (player_name, player_id, image_url))
                        print(f"✨ 신규등록: {player_name} ({image_type}) [player_id: {player_id}] -> {image_url}")
                    else:
                        sql = f"INSERT INTO photo_data (player_name, {target_column}) VALUES (%s, %s)"
                        cursor.execute(sql, (player_name, image_url))
                        print(f"✨ 신규등록: {player_name} ({image_type}) [player_id: NULL] -> {image_url}")
                    conn.commit()

            except Exception as e:
                print(f"❌ {player_name} 업로드 실패: {e}")

    finally:
        conn.close()
        print("\n🎉 모든 이미지가 S3로 이동했습니다!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='S3에 이미지 업로드 및 photo_data 테이블 업데이트')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='기존 photo_data 테이블의 모든 데이터를 삭제하고 새로 시작'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    if args.clear:
        print("⚠️  기존 데이터 삭제 모드로 실행합니다.")
    else:
        print("ℹ️  기존 데이터 유지 모드로 실행합니다. (기존 데이터 삭제하려면 --clear 옵션 사용)")
    print("=" * 60)
    print()
    
    upload_s3_and_update_db(clear_existing=args.clear)
