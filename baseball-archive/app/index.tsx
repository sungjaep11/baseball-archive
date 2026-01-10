import React, { useRef, useState } from 'react';
import {
    Animated,
    Dimensions,
    Image,
    ImageBackground,
    PanResponder,
    Platform,
    SafeAreaView,
    StatusBar,
    StyleSheet,
    Text,
    View
} from 'react-native';
import Album from '../components/album';
import NavBar from '../components/NavBar';
import PlayerSelector from '../components/player-selector';
import { Player, PlayerPosition } from '../types/player';

const { width, height } = Dimensions.get('window');

// Configuration
const DIAMOND_SIZE = width * 0.65;
const DIAMOND_OFFSET_BOTTOM = height * 0.10;
const GRASS_TEXTURE_URL = 'https://www.transparenttextures.com/patterns/grass.png';
const FIELD_GREEN = '#3a7c33';
const AUDIENCE_COLOR = 'rgba(100, 130, 150, 0.85)'; // Stadium gray-blue for the "stands" area

// Height of the sliding panel
const PANEL_HEIGHT = height * 0.85;

export default function BaseballField() {
    const slideAnim = useRef(new Animated.Value(PANEL_HEIGHT)).current;
    const [activeTab, setActiveTab] = useState<string | null>(null);
    const [isPanelOpen, setIsPanelOpen] = useState(false);
    const [selectedPlayers, setSelectedPlayers] = useState<Partial<Record<PlayerPosition, Player>>>({});

    // --- PanResponder Logic ---
    const panResponder = useRef(
        PanResponder.create({
            onMoveShouldSetPanResponder: (_, gestureState) => Math.abs(gestureState.dy) > 5,
            onPanResponderMove: (_, gestureState) => {
                if (gestureState.dy > 0) {
                    slideAnim.setValue(gestureState.dy);
                }
            },
            onPanResponderRelease: (_, gestureState) => {
                if (gestureState.dy > 150 || gestureState.vy > 0.5) {
                    closePanel();
                } else {
                    Animated.spring(slideAnim, {
                        toValue: 0,
                        useNativeDriver: true,
                        friction: 8
                    }).start();
                }
            }
        })
    ).current;

    const handleTabSelect = (tabName: string) => {
        if (isPanelOpen && activeTab === tabName) {
            closePanel();
        } else {
            setActiveTab(tabName);
            openPanel();
        }
    };

    const openPanel = () => {
        setIsPanelOpen(true);
        slideAnim.setValue(PANEL_HEIGHT);
        Animated.spring(slideAnim, {
            toValue: 0,
            useNativeDriver: true,
            friction: 8,
            tension: 40
        }).start();
    };

    const closePanel = () => {
        setIsPanelOpen(false);
        setActiveTab(null);
        Animated.timing(slideAnim, {
            toValue: PANEL_HEIGHT,
            duration: 300,
            useNativeDriver: true,
        }).start();
    };

    const handlePlayerSelect = (position: PlayerPosition, player: Player) => {
        setSelectedPlayers(prev => ({ ...prev, [position]: player }));
    };

    const getPlayerIcon = (position: PlayerPosition) => {
        return selectedPlayers[position] 
            ? require('../assets/images/player.png')
            : require('../assets/images/player-black.png');
    };

    const renderPanelContent = () => {
        switch (activeTab) {
            case 'album': return <Album />;
            case 'roster': return <PlayerSelector selectedPlayers={selectedPlayers} onPlayerSelect={handlePlayerSelect} />;
            case 'stats': return <Text style={styles.panelText}>📊 통계 (Stats Placeholder)</Text>;
            default: return null;
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="light-content" />

            {/* --- 1. Game Area (Background) --- */}
            <View style={styles.gameArea}>
                
                {/* A. AUDIENCE BACKGROUND (The dark area behind the field) */}
                <View style={[StyleSheet.absoluteFill, { backgroundColor: AUDIENCE_COLOR }]}>
                    {/* Lineup Maker Logo */}
                    <View style={styles.logoContainer}>
                        <Text style={styles.logoText}>ʟɪɴᴇᴜᴘ ᴍᴀᴋᴇʀ</Text>
                    </View>
                </View>

                {/* Baseball Field Graphics */}
                <View style={styles.fieldLayout}>
                    <View style={styles.diamondContainer}>
                        
                        {/* --- B. OUTFIELD LAYER (The Grass is now clipped inside here) --- */}
                        <View style={styles.foulLineAnchor}>
                            {/* We add overflow: 'hidden' so the grass clips to the arc shape */}
                            <View style={[styles.outfieldLine, { overflow: 'hidden', backgroundColor: FIELD_GREEN }]}>
                                
                                {/* The Grass Texture & Stripes are moved INSIDE the field shape */}
                                <ImageBackground
                                    source={{ uri: GRASS_TEXTURE_URL }}
                                    style={{ width: '100%', height: '100%' }}
                                    resizeMode="repeat"
                                    imageStyle={{ opacity: 0.4 }}
                                >
                                    <View style={styles.mowerStripesContainer}>
                                        {Array.from({ length: Math.ceil(width / 20) }).map((_, i) => (
                                            <View 
                                                key={i} 
                                                style={[
                                                    styles.mowerStripe, 
                                                    { left: i * 30, backgroundColor: i % 2 === 0 ? 'rgba(0,0,0,0.05)' : 'transparent' }
                                                ]} 
                                            />
                                        ))}
                                    </View>
                                </ImageBackground>

                            </View>
                        </View>

                        {/* Infield */}
                        <View style={styles.infieldDirt} />
                        <View style={styles.infieldGrass}>
                            <ImageBackground source={{ uri: GRASS_TEXTURE_URL }} style={{ flex: 1, opacity: 0.6 }} resizeMode="repeat" />
                        </View>
                        
                        <View style={styles.basesLayer}>
                            <View style={styles.battersBoxLeft} />
                            <View style={styles.battersBoxRight} />
                            <View style={[styles.base, styles.homePlate]} />
                            <View style={[styles.base, styles.firstBase]} />
                            <View style={[styles.base, styles.secondBase]} />
                            <View style={[styles.base, styles.thirdBase]} />
                            <View style={styles.pitchersMound}><View style={styles.pitchersRubber} /></View>
                        </View>

                        {/* Player Icons Layer */}
                        <View style={styles.playersLayer}>
                            <View style={[styles.playerContainer, styles.pitcher]}>
                                {selectedPlayers['pitcher'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['pitcher'].name} #{selectedPlayers['pitcher'].back_number}</Text></View>}
                                <Image source={getPlayerIcon('pitcher')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.catcher]}>
                                {selectedPlayers['catcher'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['catcher'].name}</Text></View>}
                                <Image source={getPlayerIcon('catcher')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.firstBaseman]}>
                                {selectedPlayers['first'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['first'].name}</Text></View>}
                                <Image source={getPlayerIcon('first')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.secondBaseman]}>
                                {selectedPlayers['second'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['second'].name}</Text></View>}
                                <Image source={getPlayerIcon('second')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.shortstop]}>
                                {selectedPlayers['shortstop'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['shortstop'].name}</Text></View>}
                                <Image source={getPlayerIcon('shortstop')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.thirdBaseman]}>
                                {selectedPlayers['third'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['third'].name}</Text></View>}
                                <Image source={getPlayerIcon('third')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.leftFielder]}>
                                {selectedPlayers['left'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['left'].name}</Text></View>}
                                <Image source={getPlayerIcon('left')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.centerFielder]}>
                                {selectedPlayers['center'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['center'].name}</Text></View>}
                                <Image source={getPlayerIcon('center')} style={styles.playerIcon} />
                            </View>
                            <View style={[styles.playerContainer, styles.rightFielder]}>
                                {selectedPlayers['right'] && <View style={styles.nameTag}><Text style={styles.nameText}>{selectedPlayers['right'].name}</Text></View>}
                                <Image source={getPlayerIcon('right')} style={styles.playerIcon} />
                            </View>
                        </View>
                    </View>
                </View>
            </View>

            {/* --- 2. Sliding Panel --- */}
            <Animated.View style={[styles.slidingPanel, { transform: [{ translateY: slideAnim }] }]}>
                <View style={styles.panelHeader} {...panResponder.panHandlers}>
                    <View style={styles.panelHandle} />
                </View>
                <View style={styles.panelBody}>
                    <Text style={styles.panelTitle}>
                        {activeTab === 'album' ? '앨범' : 
                         activeTab === 'roster' ? '선수 선택' : 
                         activeTab === 'stats' ? '통계' : ''}
                    </Text>
                    {renderPanelContent()}
                </View>
            </Animated.View>

            {/* --- 3. Navigation Bar --- */}
            <NavBar onTabSelect={handleTabSelect} activeTab={activeTab} />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: AUDIENCE_COLOR },
    gameArea: { flex: 1, position: 'relative', overflow: 'hidden' },
    
    // --- Logo Styles ---
    logoContainer: {
        position: 'absolute',
        top: height * 0.08,
        left: 0,
        right: 0,
        alignItems: 'center',
        zIndex: 5,
    },
    logoText: {
        fontSize: 36,
        fontWeight: 'normal',
        fontFamily: Platform.select({
            ios: 'Snell Roundhand',
            android: 'serif',
            web: "'Dancing Script', 'Brush Script MT', cursive",
            default: 'serif',
        }),
        color: '#ffffff',
        textShadowColor: 'rgba(0, 0, 0, 0.5)',
        textShadowOffset: { width: 2, height: 2 },
        textShadowRadius: 4,
        letterSpacing: 1,
        fontStyle: 'normal',
    },
    
    // --- Fixed Outfield Styles ---
    foulLineAnchor: {
        position: 'absolute',
        width: '100%',
        height: '100%',
        transform: [{ rotate: '45deg' }],
        zIndex: 0, 
    },
    outfieldLine: {
        position: 'absolute',
        // Scaled to fit on screen
        width: width * 1.45,  
        height: width * 1.45,
        right: 0,
        bottom: 0,
        
        borderColor: 'rgba(255, 255, 255, 0.5)', 
        borderWidth: 2, 
        
        // This radius matches the size, creating a perfect quarter-circle
        borderTopLeftRadius: width * 1.35, 
        
        backgroundColor: 'transparent',
    },

    // --- Panel Styles ---
    slidingPanel: {
        position: 'absolute', bottom: 80, width: width, height: PANEL_HEIGHT,
        backgroundColor: '#F0F4F7', borderTopLeftRadius: 30, borderTopRightRadius: 30,
        zIndex: 10, shadowColor: "#000", shadowOffset: { width: 0, height: -3 },
        shadowOpacity: 0.1, shadowRadius: 5, elevation: 15, paddingBottom: 100,
    },
    panelHeader: { width: '100%', height: 50, alignItems: 'center', justifyContent: 'center', borderBottomWidth: 1, borderBottomColor: 'rgba(100, 130, 150, 0.3)' },
    panelHandle: { width: 50, height: 6, borderRadius: 3, backgroundColor: '#7896AA' },
    panelBody: { flex: 1, paddingTop: 20 },
    panelTitle: { fontSize: 22, fontWeight: 'bold', color: '#3D5566', marginBottom: 20, paddingHorizontal: 20 },
    panelText: { fontSize: 16, color: '#424242' },

    // --- Field Styles ---
    mowerStripesContainer: { ...StyleSheet.absoluteFillObject, flexDirection: 'row' },
    mowerStripe: { width: 30, height: '100%', position: 'absolute', top: 0, bottom: 0 },
    fieldLayout: { flex: 1, alignItems: 'center', justifyContent: 'flex-end' },
    diamondContainer: { width: DIAMOND_SIZE, height: DIAMOND_SIZE, marginBottom: DIAMOND_OFFSET_BOTTOM, alignItems: 'center', justifyContent: 'center', overflow: 'visible' },
    
    infieldDirt: { width: '100%', height: '100%', backgroundColor: '#c29668', position: 'absolute', transform: [{ rotate: '45deg' }], borderRadius: 8, borderWidth: 2, borderColor: 'rgba(0,0,0,0.15)', zIndex: 5 },
    infieldGrass: { width: '70%', height: '70%', backgroundColor: '#4a9c40', position: 'absolute', transform: [{ rotate: '45deg' }], borderRadius: 4, overflow: 'hidden', zIndex: 6 },
    
    basesLayer: { width: '100%', height: '100%', position: 'absolute', zIndex: 10 },
    base: { width: 16, height: 16, backgroundColor: '#ffffff', position: 'absolute', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 1.5, elevation: 3 },
    homePlate: { bottom: -6, alignSelf: 'center', width: 18, height: 18, transform: [{ rotate: '45deg' }], borderRadius: 1 },
    firstBase: { right: -8, top: '50%', marginTop: -8, borderRadius: 1 },
    secondBase: { top: -8, alignSelf: 'center', borderRadius: 1 },
    thirdBase: { left: -8, top: '50%', marginTop: -8, borderRadius: 1 },
    battersBoxLeft: { position: 'absolute', bottom: -15, left: '50%', marginLeft: -48, width: 26, height: 48, borderWidth: 2, borderColor: 'rgba(255,255,255,0.8)' },
    battersBoxRight: { position: 'absolute', bottom: -15, left: '50%', marginLeft: 22, width: 26, height: 48, borderWidth: 2, borderColor: 'rgba(255,255,255,0.8)' },
    pitchersMound: { width: DIAMOND_SIZE * 0.18, height: DIAMOND_SIZE * 0.18, backgroundColor: '#b38a5d', borderRadius: 50, alignSelf: 'center', top: '50%', marginTop: -(DIAMOND_SIZE * 0.09), alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: 'rgba(0,0,0,0.1)', zIndex: 5 },
    pitchersRubber: { width: 14, height: 4, backgroundColor: '#ffffff', borderRadius: 1 },
    
    playersLayer: { width: '100%', height: '100%', position: 'absolute', zIndex: 20 },
    playerContainer: { position: 'absolute', alignItems: 'center', justifyContent: 'center' },
    playerIcon: { width: 130, height: 130, resizeMode: 'contain', shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 6, elevation: 8 },
    nameTag: { position: 'absolute', top: 70, backgroundColor: '#ffffff', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8, borderWidth: 2, borderColor: '#5d4037', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.3, shadowRadius: 3, elevation: 5, zIndex: 25 },
    nameText: { fontSize: 12, fontWeight: 'bold', color: '#5d4037', textAlign: 'center' },
    
    pitcher: { top: '50%', left: '50%', marginTop: -65, marginLeft: -65 },
    catcher: { bottom: -65, left: '50%', marginLeft: -65 },
    firstBaseman: { right: '-30%', top: '50%', marginTop: -65 },
    secondBaseman: { right: '2%', top: '-10%', marginTop: 0 },
    shortstop: { left: '2%', top: '-10%', marginTop: 0 },
    thirdBaseman: { left: '-30%', top: '50%', marginTop: -65 },
    leftFielder: { left: '-10%', top: '-65%', marginLeft: -20 },
    centerFielder: { left: '50%', top: '-100%', marginLeft: -65 },
    rightFielder: { right: '-10%', top: '-65%', marginRight: -20 },
});