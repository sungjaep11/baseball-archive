"""
DB 테이블의 컬럼 정보 확인 스크립트
"""

import pymysql
from pymysql.cursors import DictCursor
from config.db_config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

def check_table_columns():
    """kbo_hitters_top150와 kbo_defense_positions 테이블의 컬럼 정보 확인"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=int(DB_PORT),
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        cursor = conn.cursor()
        
        tables = {
            'kbo_hitters_top150': '타자 테이블',
            'kbo_defense_positions': '수비 포지션 테이블'
        }
        
        print("=" * 80)
        print("📊 DB 테이블 컬럼 정보 확인")
        print("=" * 80)
        
        for table_name, description in tables.items():
            print(f"\n{'='*80}")
            print(f"📋 테이블: `{table_name}` ({description})")
            print(f"{'='*80}")
            
            # 테이블 존재 여부 확인
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print(f"❌ 테이블이 존재하지 않습니다.")
                continue
            
            # 테이블 구조 확인 (DESCRIBE)
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            print(f"\n📐 테이블 구조 ({len(columns)}개 컬럼):")
            print("-" * 80)
            print(f"{'컬럼명':<25} {'데이터 타입':<25} {'NULL':<10} {'키':<10} {'기본값':<15}")
            print("-" * 80)
            
            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                col_null = col['Null']
                col_key = col['Key']
                col_default = str(col['Default']) if col['Default'] is not None else 'NULL'
                print(f"{col_name:<25} {col_type:<25} {col_null:<10} {col_key:<10} {col_default:<15}")
            
            # INFORMATION_SCHEMA로 더 자세한 정보 확인
            print(f"\n📋 상세 컬럼 정보:")
            print("-" * 80)
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE,
                    COLUMN_KEY,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (DB_NAME, table_name))
            
            detailed_columns = cursor.fetchall()
            
            for col in detailed_columns:
                print(f"\n  컬럼명: {col['COLUMN_NAME']}")
                print(f"    - 데이터 타입: {col['DATA_TYPE']}")
                print(f"    - 전체 타입: {col['COLUMN_TYPE']}")
                print(f"    - NULL 허용: {col['IS_NULLABLE']}")
                if col['COLUMN_DEFAULT']:
                    print(f"    - 기본값: {col['COLUMN_DEFAULT']}")
                if col['CHARACTER_MAXIMUM_LENGTH']:
                    print(f"    - 최대 길이: {col['CHARACTER_MAXIMUM_LENGTH']}")
                if col['NUMERIC_PRECISION']:
                    print(f"    - 숫자 정밀도: {col['NUMERIC_PRECISION']}")
                if col['NUMERIC_SCALE']:
                    print(f"    - 소수점 자릿수: {col['NUMERIC_SCALE']}")
                if col['COLUMN_KEY']:
                    print(f"    - 키 타입: {col['COLUMN_KEY']}")
                if col['EXTRA']:
                    print(f"    - 추가 정보: {col['EXTRA']}")
            
            # 샘플 데이터 확인 (처음 1행)
            print(f"\n📝 샘플 데이터 (처음 1행):")
            print("-" * 80)
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 1")
            sample = cursor.fetchone()
            
            if sample:
                for key, value in sample.items():
                    value_str = str(value) if value is not None else 'NULL'
                    if len(value_str) > 50:
                        value_str = value_str[:50] + '...'
                    print(f"  {key}: {value_str}")
            else:
                print("  (데이터 없음)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 확인 완료!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_columns()

