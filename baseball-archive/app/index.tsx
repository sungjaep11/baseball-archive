import React from 'react';
import { StyleSheet, View, Dimensions, SafeAreaView, StatusBar, ImageBackground } from 'react-native';

const { width, height } = Dimensions.get('window');

// Field Configuration
const DIAMOND_SIZE = width * 0.65;
// INCREASED from 0.15 to 0.22 to move the infield up
const DIAMOND_OFFSET_BOTTOM = height * 0.22;

// URL for a seamless grass texture
const GRASS_TEXTURE_URL = 'https://www.transparenttextures.com/patterns/grass.png';

export default function BaseballField() {

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="light-content" />

            {/* 1. Realistic Grass Background Layer */}
            <View style={StyleSheet.absoluteFill}>
                <ImageBackground
                    source={{ uri: GRASS_TEXTURE_URL }}
                    style={{ width: '100%', height: '100%', backgroundColor: '#3a7c33' }}
                    resizeMode="repeat"
                    imageStyle={{ opacity: 0.4 }}
                >
                    {/* Vertical Mower Stripes */}
                    <View style={styles.mowerStripesContainer}>
                        {Array.from({ length: Math.ceil(width / 30) }).map((_, i) => (
                            <View
                                key={i}
                                style={[
                                    styles.mowerStripe,
                                    {
                                        left: i * 30,
                                        backgroundColor: i % 2 === 0 ? 'rgba(0,0,0,0.05)' : 'transparent'
                                    }
                                ]}
                            />
                        ))}
                    </View>
                </ImageBackground>
            </View>

            {/* 2. The Main Field Container */}
            <View style={styles.fieldLayout}>

                <View style={styles.diamondContainer}>

                    {/* Dirt Square */}
                    <View style={styles.infieldDirt} />

                    {/* Inner Grass Square */}
                    <View style={styles.infieldGrass}>
                        <ImageBackground
                            source={{ uri: GRASS_TEXTURE_URL }}
                            style={{ flex: 1, opacity: 0.6 }}
                            resizeMode="repeat"
                        />
                    </View>

                    {/* Bases & Markings Layer */}
                    <View style={styles.basesLayer}>

                        {/* Batter's Boxes */}
                        <View style={styles.battersBoxLeft} />
                        <View style={styles.battersBoxRight} />

                        {/* Home Plate */}
                        <View style={[styles.base, styles.homePlate]} />

                        {/* Bases */}
                        <View style={[styles.base, styles.firstBase]} />
                        <View style={[styles.base, styles.secondBase]} />
                        <View style={[styles.base, styles.thirdBase]} />

                        {/* Pitcher's Mound */}
                        <View style={styles.pitchersMound}>
                            <View style={styles.pitchersRubber} />
                        </View>
                    </View>

                </View>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#3a7c33',
    },
    mowerStripesContainer: {
        ...StyleSheet.absoluteFillObject,
        flexDirection: 'row', // Horizontal arrangement for vertical stripes
    },
    mowerStripe: {
        width: 30,
        height: '100%',
        position: 'absolute',
        top: 0,
        bottom: 0,
    },
    fieldLayout: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'flex-end',
    },
    diamondContainer: {
        width: DIAMOND_SIZE,
        height: DIAMOND_SIZE,
        marginBottom: DIAMOND_OFFSET_BOTTOM, // This moves the field up
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'visible',
    },
    infieldDirt: {
        width: '100%',
        height: '100%',
        backgroundColor: '#c29668',
        position: 'absolute',
        transform: [{ rotate: '45deg' }],
        borderRadius: 8,
        borderWidth: 2,
        borderColor: 'rgba(0,0,0,0.15)',
    },
    infieldGrass: {
        width: '70%',
        height: '70%',
        backgroundColor: '#4a9c40',
        position: 'absolute',
        transform: [{ rotate: '45deg' }],
        borderRadius: 4,
        overflow: 'hidden',
    },
    basesLayer: {
        width: '100%',
        height: '100%',
        position: 'absolute',
    },
    base: {
        width: 16,
        height: 16,
        backgroundColor: '#ffffff',
        position: 'absolute',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 1.5,
        elevation: 3,
        zIndex: 10,
    },
    homePlate: {
        bottom: -6,
        alignSelf: 'center',
        width: 18,
        height: 18,
        transform: [{ rotate: '45deg' }],
        borderRadius: 1,
    },
    firstBase: {
        right: -8,
        top: '50%',
        marginTop: -8,
        borderRadius: 1,
    },
    secondBase: {
        top: -8,
        alignSelf: 'center',
        borderRadius: 1,
    },
    thirdBase: {
        left: -8,
        top: '50%',
        marginTop: -8,
        borderRadius: 1,
    },
    battersBoxLeft: {
        position: 'absolute',
        bottom: -15,
        left: '50%',
        marginLeft: -48,
        width: 26,
        height: 48,
        borderWidth: 2,
        borderColor: 'rgba(255,255,255,0.8)',
    },
    battersBoxRight: {
        position: 'absolute',
        bottom: -15,
        left: '50%',
        marginLeft: 22,
        width: 26,
        height: 48,
        borderWidth: 2,
        borderColor: 'rgba(255,255,255,0.8)',
    },
    pitchersMound: {
        width: DIAMOND_SIZE * 0.18,
        height: DIAMOND_SIZE * 0.18,
        backgroundColor: '#b38a5d',
        borderRadius: 50,
        alignSelf: 'center',
        top: '50%',
        marginTop: -(DIAMOND_SIZE * 0.09),
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)',
        zIndex: 5,
    },
    pitchersRubber: {
        width: 14,
        height: 4,
        backgroundColor: '#ffffff',
        borderRadius: 1,
    },
});