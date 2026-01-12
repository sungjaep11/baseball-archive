"""
데이터베이스 설정 파일 템플릿
이 파일을 복사해서 db_config.py로 만들고 실제 값으로 수정하세요.

사용법:
1. 이 파일을 db_config.py로 복사
2. 아래 값들을 실제 DB 정보로 수정
3. db_config.py는 .gitignore에 포함되어 커밋되지 않습니다.
"""

import pymysql

# ==========================================
# MySQL 데이터베이스 설정
# ==========================================
DB_HOST = 'your-db-host.rds.amazonaws.com'
DB_USER = 'your-username'
DB_PASSWORD = 'your-password'
DB_NAME = 'your-database-name'
DB_PORT = 3306

# pymysql 연결용 설정 (딕셔너리 형태)
DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'db': DB_NAME,
    'port': DB_PORT,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 60,
    'read_timeout': 300,
    'write_timeout': 300,
    'autocommit': False
}

