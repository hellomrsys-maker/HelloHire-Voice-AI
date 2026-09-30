package com.solorock.amsv;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * Java Enterprise interface to the Advanced Multi-language Shared Memory and State Vector (AMSV).
 * Uses JNI Direct ByteBuffers to achieve zero-copy synchronization with C++, Rust, Julia, and Python.
 */
public class AMSVBridge {

    private static boolean nativeLoaded = false;
    private static ByteBuffer fallbackBuffer = null;

    static {
        try {
            System.loadLibrary("amsv_core");
            nativeLoaded = true;
        } catch (UnsatisfiedLinkError e) {
            // In standalone or test environments where native lib isn't in java.library.path,
            // initialize high-performance DirectByteBuffer fallback with 64-byte alignment
            fallbackBuffer = ByteBuffer.allocateDirect(64).order(ByteOrder.nativeOrder());
            nativeLoaded = false;
        }
    }

    public static native ByteBuffer getNativeStateVectorBuffer();
    public static native ByteBuffer getNativeAudioRingBuffer();
    public static native void syncMemoryBarrier();

    /**
     * Get direct reference to the 64-byte Atomic Memory State Vector.
     */
    public static ByteBuffer getStateVector() {
        if (nativeLoaded) {
            ByteBuffer buf = getNativeStateVectorBuffer();
            if (buf != null) {
                return buf.order(ByteOrder.nativeOrder());
            }
        }
        return fallbackBuffer;
    }

    // --- TYPED SLOT READERS ---

    public static long getPhonemeState() {
        return getStateVector().getLong(0);
    }

    public static void setPhonemeState(long state) {
        getStateVector().putLong(0, state);
    }

    public static long getProsodyState() {
        return getStateVector().getLong(8);
    }

    public static void setProsodyState(long state) {
        getStateVector().putLong(8, state);
    }

    public static long getCognitiveBankAlpha() {
        return getStateVector().getLong(16);
    }

    public static long getCognitiveBankBeta() {
        return getStateVector().getLong(24);
    }

    /**
     * Read capability score (0 to 7) as float from the 16-bit fixed-point slots at bytes 16-31.
     */
    public static float getCognitiveCapabilityScore(int capabilityIndex) {
        if (capabilityIndex < 0 || capabilityIndex > 7) {
            throw new IllegalArgumentException("Capability index must be 0 to 7");
        }
        int offset = 16 + (capabilityIndex * 2);
        short raw = getStateVector().getShort(offset);
        return (float) (raw & 0xFFFF) / 65535.0f;
    }

    public static void setCognitiveCapabilityScore(int capabilityIndex, float score) {
        if (capabilityIndex < 0 || capabilityIndex > 7) {
            throw new IllegalArgumentException("Capability index must be 0 to 7");
        }
        int offset = 16 + (capabilityIndex * 2);
        short fixed = (short) Math.round(Math.max(0.0f, Math.min(1.0f, score)) * 65535.0f);
        getStateVector().putShort(offset, fixed);
    }

    public static long getScenarioState() {
        return getStateVector().getLong(32);
    }

    public static void setScenarioState(long state) {
        getStateVector().putLong(32, state);
    }

    public static long getExaminationState() {
        return getStateVector().getLong(40);
    }

    public static void setExaminationState(long state) {
        getStateVector().putLong(40, state);
    }

    public static float getExaminationIrtTheta() {
        return getStateVector().getFloat(40);
    }

    public static void setExaminationIrtTheta(float theta) {
        getStateVector().putFloat(40, theta);
    }

    public static long getMaioGlobalStateAlpha() {
        return getStateVector().getLong(48);
    }

    public static long getMaioGlobalStateBeta() {
        return getStateVector().getLong(56);
    }

    public static boolean isNativeLoaded() {
        return nativeLoaded;
    }
}
