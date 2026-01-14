# 백엔드 API 문서

## 📋 목차
1. [API 개요](#api-개요)
2. [API 엔드포인트](#api-엔드포인트)
3. [데이터베이스 구조](#데이터베이스-구조)
4. [상세 API 설명](#상세-api-설명)

---

## API 개요

### 기본 정보
- **프레임워크**: Django REST Framework
- **데이터베이스**: MySQL (AWS RDS)
- **이미지 저장소**: AWS S3
- **Base URL**: `http://localhost:8000/api/` (개발 환경)

### 주요 기능
- KBO 선수 정보 조회 (투수/타자)
- 포지션별 선수 필터링
- 선수 이미지 URL 조회 (S3)
- 실시간 통계 데이터 제공

---

## API 엔드포인트

### 1. 선수 정보 조회 (REST API)

#### 1.1 전체 선수 목록
```
GET /api/players/
```
- **설명**: 모든 선수 정보 조회 (SQLite 모델용 - 호환성 유지)
- **응답**: 선수 목록 배열

#### 1.2 특정 포지션 선수 조회
```
GET /api/players/by_position/?position={포지션}
```
- **파라미터**:
  - `position` (required): 포지션 키 (`pitcher`, `catcher`, `first`, `second`, `third`, `shortstop`, `left`, `center`, `right`)
- **예시**: `GET /api/players/by_position/?position=pitcher`
- **응답**: 해당 포지션의 선수 목록

#### 1.3 모든 포지션별 선수 조회
```
GET /api/players/all_by_position/
```
- **설명**: 모든 포지션별로 그룹화된 선수 데이터 반환
- **응답**:
```json
{
  "pitcher": [...],
  "catcher": [...],
  "first": [...],
  ...
}
```

---

### 2. MySQL 선수 데이터 조회 (KBO 크롤링 데이터)

#### 2.1 포지션별 선수 데이터
```
GET /api/mysql-players/
```
- **설명**: MySQL 테이블에서 직접 조회 (KBO 공식 사이트 크롤링 데이터)
- **데이터 소스**: 
  - 투수: `kbo_pitchers_top150` 테이블
  - 타자: `kbo_hitters_top150` + `kbo_defense_positions` JOIN
- **응답 형식**:
```json
{
  "pitcher": [
    {
      "id": 1001,
      "name": "류현진",
      "team": "한화 이글스",
      "position": "pitcher",
      "back_number": 1,
      "era": 3.45,
      "wins": 15,
      "losses": 8,
      "holds": 0,
      "saves": 0,
      "strikeouts": 180,
      "whip": 1.20
    },
    ...
  ],
  "catcher": [...],
  "first": [...],
  ...
}
```

**포지션 ID 오프셋**:
- `pitcher`: 1000번대
- `catcher`: 2000번대
- `first`: 3000번대
- `second`: 4000번대
- `third`: 5000번대
- `shortstop`: 6000번대
- `left`: 7000번대
- `center`: 8000번대
- `right`: 9000번대

**투수 통계 필드**:
- `era`: 평균자책점
- `wins`: 승
- `losses`: 패
- `holds`: 홀드
- `saves`: 세이브
- `strikeouts`: 탈삼진
- `whip`: WHIP (이닝당 출루 허용)

**타자 통계 필드**:
- `batting_average`: 타율
- `rbis`: 타점
- `home_runs`: 홈런
- `stolen_bases`: 득점 (도루 대신 득점 사용)

---

### 3. 선수 이미지 조회 (S3 URL)

#### 3.1 선수 이미지 목록
```
GET /api/player-images/?names={선수명1}&names={선수명2}&...
```
- **설명**: 선택된 선수들의 이미지 URL 조회 (S3)
- **파라미터**:
  - `names` (required, multiple): 선수 이름 목록 (여러 개 가능)
- **예시**: `GET /api/player-images/?names=류현진&names=김광현`
- **응답 형식**:
```json
[
  {
    "id": "류현진_1",
    "playerName": "류현진",
    "playerId": 1001,
    "imageUrl": "https://s3...amazonaws.com/players/류현진_1.jpg",
    "fileName": "류현진_1.jpg",
    "imageType": "1"
  },
  {
    "id": "류현진_2",
    "playerName": "류현진",
    "playerId": 1001,
    "imageUrl": "https://s3...amazonaws.com/players/류현진_2.jpg",
    "fileName": "류현진_2.jpg",
    "imageType": "2"
  },
  {
    "id": "류현진_profile",
    "playerName": "류현진",
    "playerId": 1001,
    "imageUrl": "https://s3...amazonaws.com/players/류현진_profile.jpg",
    "fileName": "류현진_profile.jpg",
    "imageType": "profile"
  },
  ...
]
```

**이미지 타입**:
- `1`, `2`, `3`: 갤러리 이미지 (앨범 탭용)
- `profile`: 프로필 이미지 (프로필 카드용)

**데이터 소스**: `photo_data` 테이블
- `image_1`, `image_2`, `image_3`: 갤러리 이미지 S3 URL
- `profile_img`: 프로필 이미지 S3 URL

---

## 데이터베이스 구조

### 주요 테이블

#### 1. `kbo_hitters_top150`
- **설명**: KBO 타자 상위 150명 통계 데이터
- **주요 컬럼**: `순위`, `선수명`, `팀명`, `AVG`, `HR`, `RBI`, `R`, `player_id`, `image_data`

#### 2. `kbo_pitchers_top150`
- **설명**: KBO 투수 상위 150명 통계 데이터
- **주요 컬럼**: `순위`, `선수명`, `팀명`, `ERA`, `W`, `L`, `SV`, `HLD`, `SO`, `WHIP`, `player_id`, `image_data`

#### 3. `kbo_defense_positions`
- **설명**: 타자의 수비 포지션 정보
- **주요 컬럼**: `선수명`, `팀명`, `포지션` (한글)

#### 4. `photo_data`
- **설명**: 선수 이미지 S3 URL 저장
- **주요 컬럼**:
  - `id`: 기본 키
  - `player_id`: 선수 ID
  - `player_name`: 선수명
  - `image_1`, `image_2`, `image_3`: 갤러리 이미지 S3 URL (VARCHAR)
  - `profile_img`: 프로필 이미지 S3 URL (VARCHAR)

---

## 상세 API 설명

### 포지션 매핑

**DB 포지션 → 프론트엔드 포지션**:
```python
{
    'P': 'pitcher',
    'C': 'catcher',
    '1B': 'first',
    '2B': 'second',
    '3B': 'third',
    'SS': 'shortstop',
    'LF': 'left',
    'CF': 'center',
    'RF': 'right',
}
```

**한글 포지션 → 영문 포지션**:
```python
{
    '포수': 'C',
    '1루수': '1B',
    '2루수': '2B',
    '3루수': '3B',
    '유격수': 'SS',
    '좌익수': 'LF',
    '중견수': 'CF',
    '우익수': 'RF',
    '지명타자': 'DH',
}
```

---

## 에러 처리

### 공통 에러 응답 형식
```json
{
  "error": "에러 메시지",
  "detail": "상세 설명"
}
```

### HTTP 상태 코드
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청 (필수 파라미터 누락 등)
- `404 Not Found`: 리소스를 찾을 수 없음
- `500 Internal Server Error`: 서버 내부 오류

---

## 사용 예시

### 1. 투수 목록 가져오기
```bash
curl http://localhost:8000/api/mysql-players/
```

### 2. 특정 선수 이미지 가져오기
```bash
curl "http://localhost:8000/api/player-images/?names=류현진&names=김광현"
```

### 3. 포지션별 선수 조회
```bash
curl "http://localhost:8000/api/players/by_position/?position=pitcher"
```

---

## 설정 파일

### 데이터베이스 설정
- **파일**: `backend/config/db_config.py` (gitignore에 포함)
- **예시 파일**: `backend/config/db_config.example.py`

### AWS S3 설정
- **파일**: `backend/config/aws_config.py` (gitignore에 포함)
- **예시 파일**: `backend/config/aws_config.example.py`

---

## 개발 환경 실행

```bash
cd backend
python manage.py runserver
```

서버가 `http://localhost:8000`에서 실행됩니다.

---

## 참고사항

1. **CORS 설정**: 개발 환경에서는 모든 origin 허용 (`CORS_ALLOW_ALL_ORIGINS = True`)
2. **미디어 파일**: 개발 환경에서만 `/media/` 경로로 제공
3. **인증**: 현재 모든 API는 인증 없이 접근 가능 (개발 환경)
4. **이미지 저장**: 모든 이미지는 AWS S3에 저장되며, DB에는 URL만 저장

