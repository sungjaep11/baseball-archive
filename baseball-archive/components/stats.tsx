import React, { useMemo } from 'react';
import {
  Dimensions,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import Svg, { G, Path, Text as SvgText } from 'react-native-svg';
import { Player, PlayerPosition } from '../types/player';

const { width } = Dimensions.get('window');

interface StatsProps {
  selectedPlayers: Partial<Record<PlayerPosition, Player>>;
}

interface TeamStats {
  // 타자 통계
  battingAvg: number; // 타율
  rbis: number; // 타점
  homeRuns: number; // 홈런
  stolenBases: number; // 도루
  
  // 투수 통계
  era: number; // 평균자책점
  wins: number; // 승
  losses: number; // 패
  saves: number; // 세이브
  holds: number; // 홀드
  strikeouts: number; // 탈삼진
  
}

interface TeamAbilities {
  power: number; // 파워 (0-100)
  accuracy: number; // 정확도 (0-100)
  running: number; // 주루 (0-100)
  defense: number; // 수비 (0-100)
  pitching: number; // 투수력 (0-100)
}

export default function Stats({ selectedPlayers }: StatsProps) {
  // 선택된 선수 중 타자와 투수 분리
  const batters = useMemo(() => {
    const positions: PlayerPosition[] = ['catcher', 'first', 'second', 'shortstop', 'third', 'left', 'center', 'right'];
    return positions
      .map(pos => selectedPlayers[pos])
      .filter((p): p is Player => p !== undefined);
  }, [selectedPlayers]);

  const pitchers = useMemo(() => {
    const pitcher = selectedPlayers['pitcher'];
    return pitcher ? [pitcher] : [];
  }, [selectedPlayers]);

  // 통계 계산
  const teamStats = useMemo((): TeamStats => {
    const stats: TeamStats = {
      battingAvg: 0,
      rbis: 0,
      homeRuns: 0,
      stolenBases: 0,
      era: 0,
      wins: 0,
      losses: 0,
      saves: 0,
      holds: 0,
      strikeouts: 0,
    };

    if (batters.length > 0) {
      // 타자 통계 평균 계산
      const totalAvg = batters.reduce((sum, p) => sum + (p.batting_average || 0), 0);
      const totalRbis = batters.reduce((sum, p) => sum + (p.rbis || 0), 0);
      const totalHr = batters.reduce((sum, p) => sum + (p.home_runs || 0), 0);
      const totalSb = batters.reduce((sum, p) => sum + (p.stolen_bases || 0), 0);

      stats.battingAvg = totalAvg / batters.length;
      stats.rbis = totalRbis / batters.length;
      stats.homeRuns = totalHr / batters.length;
      stats.stolenBases = totalSb / batters.length;
    }

    if (pitchers.length > 0) {
      // 투수 통계 평균 계산
      const totalEra = pitchers.reduce((sum, p) => sum + (p.era || 0), 0);
      const totalWins = pitchers.reduce((sum, p) => sum + (p.wins || 0), 0);
      const totalLosses = pitchers.reduce((sum, p) => sum + (p.losses || 0), 0);
      const totalSaves = pitchers.reduce((sum, p) => sum + (p.saves || 0), 0);
      const totalHolds = pitchers.reduce((sum, p) => sum + (p.holds || 0), 0);
      const totalK = pitchers.reduce((sum, p) => sum + (p.strikeouts || 0), 0);

      stats.era = totalEra / pitchers.length;
      stats.wins = totalWins / pitchers.length;
      stats.losses = totalLosses / pitchers.length;
      stats.saves = totalSaves / pitchers.length;
      stats.holds = totalHolds / pitchers.length;
      stats.strikeouts = totalK / pitchers.length;
    }

    return stats;
  }, [batters, pitchers]);

  // 팀 능력치 계산 (0-100 스케일)
  const teamAbilities = useMemo((): TeamAbilities => {
    // 파워: 홈런 기준 (0-60개를 0-100으로 변환)
    const power = Math.min(100, (teamStats.homeRuns / 60) * 100);

    // 정확도: 타율 기준 (0-0.400을 0-100으로 변환)
    const accuracy = Math.min(100, (teamStats.battingAvg / 0.400) * 100);

    // 주루: 도루 기준 (0-50개를 0-100으로 변환)
    const running = Math.min(100, (teamStats.stolenBases / 50) * 100);

    // 수비: 타율과 홈런 기반 (간단한 계산)
    const defense = (accuracy * 0.6 + power * 0.4);

    // 투수력: ERA 기준 (0-6.0을 역으로 100-0으로 변환, 낮을수록 좋음)
    const pitching = teamStats.era > 0 
      ? Math.max(0, Math.min(100, ((6.0 - teamStats.era) / 6.0) * 100))
      : 50; // ERA 데이터가 없으면 평균값

    return {
      power: Math.round(power),
      accuracy: Math.round(accuracy),
      running: Math.round(running),
      defense: Math.round(defense),
      pitching: Math.round(pitching),
    };
  }, [teamStats]);

  // 예상 승률 계산 (피타고라스 승률 비슷한 방식)
  const expectedWinRate = useMemo(() => {
    const abilities = teamAbilities;
    
    // 능력치 기반 승률 계산 (간단한 공식)
    // 공격력(파워, 정확도, 주루)과 수비력(수비, 투수력)의 평균
    const offense = (abilities.power + abilities.accuracy + abilities.running) / 3;
    const defense = (abilities.defense + abilities.pitching) / 2;
    const totalAbility = (offense * 0.5 + defense * 0.5) / 100;

    // 0.4 ~ 0.6 범위로 정규화 (최소 0.4, 최대 0.6)
    const winRate = 0.4 + (totalAbility * 0.2);
    return Math.max(0.3, Math.min(0.7, winRate));
  }, [teamAbilities]);

  // 팀 성향 분석
  const teamAnalysis = useMemo(() => {
    const { power, accuracy, running, defense, pitching } = teamAbilities;
    
    const traits: string[] = [];
    
    if (power >= 70) {
      traits.push('거포');
    }
    if (running >= 70) {
      traits.push('주루');
    }
    if (accuracy >= 70 && power >= 60) {
      traits.push('타격');
    }
    if (pitching >= 70) {
      traits.push('투수');
    }
    if (defense >= 70) {
      traits.push('수비');
    }
    
    if (traits.length === 0) {
      return '균형잡힌';
    }
    
    return traits.join('·');
  }, [teamAbilities]);

  // 승률 멘트
  const winRateMessage = useMemo(() => {
    if (expectedWinRate >= 0.600) {
      return '이대로면 한국시리즈 우승 확정!';
    } else if (expectedWinRate >= 0.500) {
      return '가을야구 진출이 유력합니다.';
    } else if (expectedWinRate >= 0.400) {
      return '중위권 싸움이 치열하겠네요.';
    } else {
      return '리빌딩이 시급합니다...';
    }
  }, [expectedWinRate]);

  // 오각형 그래프 컴포넌트
  const PentagonChart = ({ abilities, size = 200 }: { abilities: TeamAbilities; size?: number }) => {
    const center = size / 2;
    const radius = size / 2 - 30;
    const angles = [90, 18, -54, -126, -198]; // 5개 꼭짓점의 각도 (도 단위)

    // 각 능력치를 좌표로 변환
    const points = angles.map((angle, index) => {
      const value = [
        abilities.power,
        abilities.accuracy,
        abilities.running,
        abilities.defense,
        abilities.pitching
      ][index];
      const rad = (angle * Math.PI) / 180;
      const distance = (value / 100) * radius;
      const x = center + distance * Math.cos(rad);
      const y = center - distance * Math.sin(rad);
      return { x, y };
    });

    // 폴리곤 경로 생성
    const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';

    // 격자선 그리기
    const gridLines = [0.25, 0.5, 0.75, 1.0].map(scale => {
      const gridPoints = angles.map(angle => {
        const rad = (angle * Math.PI) / 180;
        const distance = scale * radius;
        const x = center + distance * Math.cos(rad);
        const y = center - distance * Math.sin(rad);
        return { x, y };
      });
      const gridPath = gridPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
      return gridPath;
    });

    return (
      <View style={styles.chartContainer}>
        <Svg width={size} height={size}>
          {/* 격자선 */}
          {gridLines.map((path, i) => (
            <Path key={i} d={path} fill="none" stroke="#E0E0E0" strokeWidth="1" opacity={0.5} />
          ))}
          
          {/* 능력치 영역 */}
          <Path
            d={pathData}
            fill="#7896AA"
            fillOpacity={0.4}
            stroke="#7896AA"
            strokeWidth="2"
          />
          
          {/* 축선 */}
          {angles.map((angle, index) => {
            const rad = (angle * Math.PI) / 180;
            const x = center + radius * Math.cos(rad);
            const y = center - radius * Math.sin(rad);
            const labels = ['파워', '정확도', '주루', '수비', '투수력'];
            const labelX = center + (radius + 20) * Math.cos(rad);
            const labelY = center - (radius + 20) * Math.sin(rad);
            
            return (
              <G key={index}>
                <Path
                  d={`M ${center} ${center} L ${x} ${y}`}
                  stroke="#BDBDBD"
                  strokeWidth="1"
                  opacity={0.3}
                />
                <SvgText
                  x={labelX}
                  y={labelY + 4}
                  fontSize="12"
                  fill="#424242"
                  textAnchor="middle"
                >
                  {labels[index]}
                </SvgText>
              </G>
            );
          })}
        </Svg>
      </View>
    );
  };

  const hasData = batters.length > 0 || pitchers.length > 0;

  if (!hasData) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>선수를 선택하면 통계가 표시됩니다.</Text>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={true}
    >
      {/* 타자 통계 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>타자 통계</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>타율</Text>
            <Text style={styles.statValue}>{teamStats.battingAvg.toFixed(3)}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>타점</Text>
            <Text style={styles.statValue}>{teamStats.rbis.toFixed(1)}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>홈런</Text>
            <Text style={styles.statValue}>{teamStats.homeRuns.toFixed(1)}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>도루</Text>
            <Text style={styles.statValue}>{teamStats.stolenBases.toFixed(1)}</Text>
          </View>
        </View>
      </View>

      {/* 투수 통계 */}
      {pitchers.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>투수 통계</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>평균자책점</Text>
              <Text style={styles.statValue}>{teamStats.era.toFixed(2)}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>승</Text>
              <Text style={styles.statValue}>{teamStats.wins.toFixed(1)}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>패</Text>
              <Text style={styles.statValue}>{teamStats.losses.toFixed(1)}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>세이브</Text>
              <Text style={styles.statValue}>{teamStats.saves.toFixed(1)}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>홀드</Text>
              <Text style={styles.statValue}>{teamStats.holds.toFixed(1)}</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statLabel}>탈삼진</Text>
              <Text style={styles.statValue}>{teamStats.strikeouts.toFixed(1)}</Text>
            </View>
          </View>
        </View>
      )}

      {/* 팀 능력치 오각형 그래프 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>팀 능력치</Text>
        <PentagonChart abilities={teamAbilities} />
        <View style={styles.teamAnalysis}>
          <Text style={styles.teamAnalysisText}>
            이 팀은 <Text style={styles.teamTrait}>{teamAnalysis}</Text> 팀입니다.
          </Text>
        </View>
      </View>

      {/* 예상 승률 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>예상 승률</Text>
        <View style={styles.winRateContainer}>
          <Text style={styles.winRateValue}>{(expectedWinRate * 100).toFixed(1)}%</Text>
          <Text style={styles.winRateMessage}>{winRateMessage}</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  content: {
    paddingBottom: 40,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 16,
    color: '#757575',
    textAlign: 'center',
  },
  section: {
    marginBottom: 30,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#3D5566',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: (width - 60) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statLabel: {
    fontSize: 14,
    color: '#757575',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3D5566',
  },
  chartContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 20,
  },
  chartLegend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 12,
    gap: 20,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legendColor: {
    width: 16,
    height: 16,
    borderRadius: 8,
    marginRight: 8,
  },
  legendText: {
    fontSize: 14,
    color: '#424242',
  },
  teamAnalysis: {
    marginTop: 20,
    padding: 16,
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
  },
  teamAnalysisText: {
    fontSize: 16,
    color: '#424242',
    textAlign: 'center',
  },
  teamTrait: {
    fontWeight: 'bold',
    color: '#1976D2',
  },
  winRateContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  winRateValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#7896AA',
    marginBottom: 12,
  },
  winRateMessage: {
    fontSize: 18,
    color: '#424242',
    textAlign: 'center',
  },
});
