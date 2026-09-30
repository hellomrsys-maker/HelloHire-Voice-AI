/**
 * @file amsv_jni_bridge.cpp
 * @brief Implementation of JNI bridge exposing AMSV direct byte buffers to Java.
 */

#include "../include/amsv_jni_bridge.h"
#include "../include/amsv_layout.h"

extern "C" void* amsv_get_atomic_state_vector();
extern "C" void* amsv_get_audio_ring_buffer();

JNIEXPORT jobject JNICALL Java_com_solorock_amsv_AMSVBridge_getNativeStateVectorBuffer
  (JNIEnv *env, jclass) {
    void* pVector = amsv_get_atomic_state_vector();
    if (!pVector) return nullptr;
    // Return a direct byte buffer of exactly 64 bytes wrapping the physical vector address
    return env->NewDirectByteBuffer(pVector, sizeof(solorock::amsv::AtomicStateVector));
}

JNIEXPORT jobject JNICALL Java_com_solorock_amsv_AMSVBridge_getNativeAudioRingBuffer
  (JNIEnv *env, jclass) {
    void* pRing = amsv_get_audio_ring_buffer();
    if (!pRing) return nullptr;
    return env->NewDirectByteBuffer(pRing, sizeof(solorock::amsv::LockFreeAudioRingBuffer));
}

JNIEXPORT void JNICALL Java_com_solorock_amsv_AMSVBridge_syncMemoryBarrier
  (JNIEnv *, jclass) {
    solorock::amsv::memory_fence_seq_cst();
}
