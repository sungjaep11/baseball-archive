import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Player, PlayerPosition, POSITION_NAMES, getPlayersByPosition } from '../types/player';

export default function PlayerSelector() {
  // 어떤 포지션이 펼쳐져 있는지 저장
  const [expandedPosition, setExpandedPosition] = useState<PlayerPosition | null>(null);
  
  // 각 포지션별로 선택된 선수 저장 (포지션: 선수)
  const [selectedPlayers, setSelectedPlayers] = useState<Record<PlayerPosition, Player | null>>({
    pitcher: null,
    catcher: null,
    first: null,
    second: null,
    shortstop: null,
    third: null,
    left: null,
    center: null,
    right: null,
  });

  // 모든 포지션 목록
  const positions: PlayerPosition[] = [
    'pitcher',
    'catcher',
    'first',
    'second',
    'shortstop',
    'third',
    'left',
    'center',
    'right',
  ];

  // 포지션 펼치기/접기
  const togglePosition = (position: PlayerPosition) => {
    if (expandedPosition === position) {
      // 같은 포지션 클릭 → 접기
      setExpandedPosition(null);
    } else {
      // 다른 포지션 클릭 → 펼치기
      setExpandedPosition(position);
    }
  };

  // 선수 선택
  const handlePlayerSelect = (position: PlayerPosition, player: Player) => {
    // 해당 포지션의 선수 저장
    setSelectedPlayers({
      ...selectedPlayers,
      [position]: player,
    });
    
    // 선택 후 자동으로 리스트 닫기
    setExpandedPosition(null);
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>선수 선택</Text>
        <Text style={styles.subtitle}>각 포지션별로 선수를 선택하세요</Text>
      </View>

      {/* 포지션 리스트 (세로로 나열) */}
      <ScrollView style={styles.scrollView}>
        {positions.map((position) => {
          const players = getPlayersByPosition(position);
          const expanded = expandedPosition === position;
          const selectedPlayer = selectedPlayers[position];

          return (
            <View key={position} style={styles.positionSection}>
              {/* 포지션 헤더 (클릭 가능) */}
              <TouchableOpacity
                style={[
                  styles.positionHeader,
                  expanded && styles.positionHeaderExpanded,
                ]}
                onPress={() => togglePosition(position)}>
                <View style={styles.positionHeaderLeft}>
                  <Text style={styles.positionIcon}>
                    {expanded ? '▼' : '▶'}
                  </Text>
                  <Text style={styles.positionName}>
                    {POSITION_NAMES[position]}
                  </Text>
                </View>

                {/* 선택된 선수 정보 표시 */}
                <View style={styles.selectedPlayerInfo}>
                  {selectedPlayer ? (
                    <>
                      <Text style={styles.selectedPlayerName}>
                        {selectedPlayer.name}
                      </Text>
                      <Text style={styles.selectedPlayerDetail}>
                        #{selectedPlayer.backNumber}
                      </Text>
                    </>
                  ) : (
                    <Text style={styles.noSelection}>선택 안됨</Text>
                  )}
                </View>
              </TouchableOpacity>

              {/* 선수 리스트 (펼쳐진 경우만 표시) */}
              {expanded && (
                <View style={styles.playerListContainer}>
                  {players.map((player) => (
                    <TouchableOpacity
                      key={player.id}
                      style={[
                        styles.playerCard,
                        selectedPlayer?.id === player.id && styles.selectedCard,
                      ]}
                      onPress={() => handlePlayerSelect(position, player)}>
                      <View style={styles.checkboxContainer}>
                        <View style={[
                          styles.checkbox,
                          selectedPlayer?.id === player.id && styles.checkboxSelected,
                        ]}>
                          {selectedPlayer?.id === player.id && (
                            <Text style={styles.checkmark}>✓</Text>
                          )}
                        </View>
                      </View>
                      
                      <View style={styles.playerInfo}>
                        <View style={styles.playerHeader}>
                          <Text style={styles.playerName}>{player.name}</Text>
                          <Text style={styles.backNumber}>#{player.backNumber}</Text>
                        </View>
                        <Text style={styles.teamName}>{player.team}</Text>
                      </View>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#666666',
  },
  scrollView: {
    flex: 1,
  },
  positionSection: {
    marginBottom: 1,
  },
  positionHeader: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
    minHeight: 60,
    borderRadius: 12,
    marginHorizontal: 12,
    marginVertical: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  positionHeaderExpanded: {
    backgroundColor: '#E3F2FD',
    borderBottomColor: '#2196F3',
    borderBottomWidth: 2,
  },
  positionHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 0,
  },
  positionIcon: {
    fontSize: 14,
    color: '#2196F3',
    marginRight: 12,
    width: 20,
  },
  positionName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
    minWidth: 60,
  },
  selectedPlayerInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginLeft: 16,
  },
  selectedPlayerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2196F3',
    marginRight: 6,
  },
  selectedPlayerDetail: {
    fontSize: 14,
    color: '#666666',
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  noSelection: {
    fontSize: 14,
    color: '#AAAAAA',
    fontStyle: 'italic',
  },
  playerListContainer: {
    backgroundColor: '#FAFAFA',
    paddingVertical: 8,
  },
  playerCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 16,
    marginVertical: 6,
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  selectedCard: {
    borderWidth: 2,
    borderColor: '#2196F3',
    backgroundColor: '#E3F2FD',
  },
  checkboxContainer: {
    marginRight: 12,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#CCCCCC',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  checkboxSelected: {
    backgroundColor: '#2196F3',
    borderColor: '#2196F3',
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  playerInfo: {
    flex: 1,
  },
  playerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  playerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333333',
    marginRight: 8,
  },
  backNumber: {
    fontSize: 14,
    color: '#666666',
    fontWeight: '600',
  },
  teamName: {
    fontSize: 13,
    color: '#888888',
  },
});
