import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';

interface NavBarProps {
    onTabSelect: (tabName: string) => void;
    activeTab?: string | null;
}

export default function NavBar({ onTabSelect, activeTab = null }: NavBarProps) {
    const handleTabPress = (tabName: string) => {
        onTabSelect(tabName);
    };

    return (
        <View style={styles.container}>
            {/* 1. Album Button */}
            <TouchableOpacity
                style={styles.iconContainer}
                onPress={() => handleTabPress('album')}
                activeOpacity={0.7}
            >
                <View style={[
                    styles.iconCircle,
                    activeTab === 'album' && styles.activeIconCircle
                ]}>
                    <Ionicons 
                        name="images-outline" 
                        size={24} 
                        color={activeTab === 'album' ? '#212121' : '#424242'} 
                    />
                </View>
            </TouchableOpacity>

            {/* 2. Roster Button */}
            <TouchableOpacity
                style={styles.iconContainer}
                onPress={() => handleTabPress('roster')}
                activeOpacity={0.7}
            >
                <View style={[
                    styles.iconCircle,
                    activeTab === 'roster' && styles.activeIconCircle
                ]}>
                    <Ionicons 
                        name="people-outline" 
                        size={24} 
                        color={activeTab === 'roster' ? '#212121' : '#424242'} 
                    />
                </View>
            </TouchableOpacity>

            {/* 3. Stats Button */}
            <TouchableOpacity
                style={styles.iconContainer}
                onPress={() => handleTabPress('stats')}
                activeOpacity={0.7}
            >
                <View style={[
                    styles.iconCircle,
                    activeTab === 'stats' && styles.activeIconCircle
                ]}>
                    <Ionicons 
                        name="stats-chart-outline" 
                        size={24} 
                        color={activeTab === 'stats' ? '#212121' : '#424242'} 
                    />
                </View>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        height: 90,
        backgroundColor: '#F0F4F7', // Light gray-blue background to match audience theme
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
        justifyContent: 'space-around',
        alignItems: 'center',
        paddingHorizontal: 10,
        paddingBottom: 24,
        paddingTop: 14,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 8,
        zIndex: 20,
    },
    iconContainer: {
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
    },
    iconCircle: {
        width: 48,
        height: 48,
        borderRadius: 24,
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'transparent',
        overflow: 'hidden',
    },
    activeIconCircle: {
        backgroundColor: '#7896AA', // Gray-blue background for active icon to match audience theme
        borderRadius: 24,
    },
});