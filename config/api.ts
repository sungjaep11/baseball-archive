/**
 * API 설정 파일
 * Django 백엔드 서버와 통신하기 위한 설정
 */

import { Platform } from 'react-native';

// 환경에 따른 API URL 설정
const getApiUrl = () => {
  if (__DEV__) {
    // 개발 환경
    if (Platform.OS === 'android') {
      // Android 에뮬레이터: 10.0.2.2는 호스트 머신의 localhost를 가리킴
      // 실제 Android 기기: 컴퓨터의 로컬 IP 주소 사용 필요 (예: 'http://192.168.0.100:8000')
      return 'http://10.0.2.2:8000';
    } else if (Platform.OS === 'ios') {
      // iOS 시뮬레이터: localhost 사용 가능
      // 실제 iOS 기기: 컴퓨터의 로컬 IP 주소 사용 필요
      return 'http://localhost:8000';
    }
    // 기본값 (웹 등)
    return 'http://localhost:8000';
  }
  
  // 프로덕션 환경 (실제 배포 시)
  //return 'https://your-production-api.com';
  return 'http://localhost:8000';
};

export const API_URL = getApiUrl();

// API 엔드포인트
export const API_ENDPOINTS = {
  // 기존 SQLite 기반 API (호환성 유지)
  players: `${API_URL}/api/players/`,
  playersByPosition: (position: string) => `${API_URL}/api/players/by_position/?position=${position}`,
  allPlayersByPosition: `${API_URL}/api/players/all_by_position/`,
  playerDetail: (id: number) => `${API_URL}/api/players/${id}/`,
  
  // MySQL 테이블 직접 쿼리 API (batterlist, pitcherlist)
  mysqlPlayers: `${API_URL}/api/mysql-players/`,
  
  // 타자 최근 경기 기록 API
  hitterRecentGames: (playerName: string) => `${API_URL}/api/hitter-recent-games/?player_name=${encodeURIComponent(playerName)}`,
  // 투수 최근 경기 기록 API
  pitcherRecentGames: (playerName: string) => `${API_URL}/api/pitcher-recent-games/?player_name=${encodeURIComponent(playerName)}`,
  // 2025 타자 목록 API
  hitters2025: `${API_URL}/api/hitters-2025/`,
  // 2025 투수 목록 API
  pitchers2025: `${API_URL}/api/pitchers-2025/`,
  // 타자 vs 투수 시뮬레이션 API
  simulateAtBat: `${API_URL}/api/simulate-at-bat/`,
};

// API 호출 시 공통으로 사용할 헤더
export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

