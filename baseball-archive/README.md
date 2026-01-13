# ⚾ Baseball Archive - 라인업 메이커

KBO 리그 선수 데이터를 활용한 야구 라인업 구성 및 통계 분석 애플리케이션입니다.

## 📱 주요 기능

### 1. **라인업 구성**
- 포지션별 선수 선택 (포수, 내야수, 외야수)
- 선발 투수 및 불펜 투수 선택
- 야구장 배경에 선수 아이콘 배치
- 선수 아이콘 클릭 시 상세 프로필 확인

### 2. **통계 분석**
- 타자 평균 기록 (타율, 타점, 홈런, 득점)
- 투수 기록 (평균자책점, 승/패, 세이브, 홀드, 탈삼진)
- 팀 능력치 오각형 그래프
- 최적의 타순 추천
- 예상 승률 및 순위 계산

### 3. **선수 프로필**
- 선수 상세 정보 (이름, 팀, 포지션)
- 주요 통계 표시
- 타자/투수별 오각형 능력치 그래프
  - **타자**: 파워, 정확도, 득점력, 수비, 체력
  - **투수**: 제구, 탈삼진 능력, 피안타 억제력, 위기관리, 체력
- 팀 로고 표시

### 4. **앨범**
- 선택한 선수들의 사진 갤러리
- 선수별 필터링 기능
- 이미지 확대 보기

## 🛠 기술 스택

### 프론트엔드
- **React Native** (Expo)
- **TypeScript**
- **expo-blur** (Glassmorphism 효과)
- **react-native-svg** (오각형 그래프)
- **React Hooks** (useState, useMemo, useEffect)

### 백엔드
- **Django REST Framework**
- **MySQL** (AWS RDS)
- KBO 공식 사이트 크롤링 데이터

### 데이터베이스
- `kbo_hitters_top150` - 타자 통계
- `kbo_pitchers_top150` - 투수 통계
- `kbo_defense_positions` - 포지션 정보

## 🎨 디자인 특징

- **Glassmorphism** 테마 적용
  - 네비게이션 바
  - 슬라이딩 패널
  - 통계 카드
  - 선수 선택 필터
  - 프로필 카드
- 부드러운 슬라이딩 애니메이션
- 직관적인 터치 제스처 지원

## 📦 설치 및 실행

### 필수 요구사항
- Node.js 18+
- Python 3.8+
- MySQL 8.0+
- Expo CLI

### 프론트엔드 설정

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm start

# iOS 시뮬레이터에서 실행
npm run ios

# Android 에뮬레이터에서 실행
npm run android
```

### 백엔드 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```

## 📁 프로젝트 구조

```
baseball-archive/
├── app/                    # Expo Router 앱 페이지
│   └── index.tsx          # 메인 야구장 화면
├── components/            # 재사용 가능한 컴포넌트
│   ├── NavBar.tsx         # 하단 네비게이션 바
│   ├── player-selector.tsx # 선수 선택 화면
│   ├── stats.tsx          # 통계 화면
│   ├── profile.tsx        # 선수 프로필 모달
│   └── album.tsx          # 선수 사진 앨범
├── backend/               # Django 백엔드
│   ├── baseball/
│   │   └── views.py      # API 엔드포인트
│   └── config/
│       └── settings.py   # Django 설정
├── assets/               # 이미지 및 리소스
│   └── images/
│       └── logos/        # 팀 로고
└── types/                # TypeScript 타입 정의
    └── player.ts         # Player 인터페이스
```

## 🔌 API 엔드포인트

- `GET /api/mysql-players/` - 포지션별 선수 목록 조회
- `GET /api/player-images/` - 선수 이미지 목록 조회

## 📊 데이터 소스

- KBO 공식 사이트 크롤링 데이터 (2024 시즌)
- 타자 상위 150명
- 투수 상위 150명

## 🎯 주요 기능 상세

### 능력치 계산 방식

**타자:**
- 파워: 홈런 기준 (0-50개 → 0-100)
- 정확도: 타율 기준 (0-0.400 → 0-100)
- 득점력: 득점 기준 (0-100점 → 0-100)
- 수비: 타율과 홈런 기반
- 체력: 타점과 득점 기반

**투수:**
- 제구: ERA 기준 (낮을수록 좋음)
- 탈삼진 능력: 탈삼진 개수 기준
- 피안타 억제력: ERA와 탈삼진 기반
- 위기관리: WHIP + ERA 역정규화
- 체력: 승/세이브/홀드 합계 기반
