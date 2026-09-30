/**
 * @file amsv_jni_bridge.h
 * @brief JNI Native Interface for Java Enterprise Layer to access AMSV with Zero Serialization.
 */

#ifndef AMSV_JNI_BRIDGE_H
#define AMSV_JNI_BRIDGE_H

#include <jni.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Class:     com_solorock_amsv_AMSVBridge
 * Method:    getNativeStateVectorBuffer
 * Signature: ()Ljava/nio/ByteBuffer;
 */
JNIEXPORT jobject JNICALL Java_com_solorock_amsv_AMSVBridge_getNativeStateVectorBuffer
  (JNIEnv *env, jclass cls);

/*
 * Class:     com_solorock_amsv_AMSVBridge
 * Method:    getNativeAudioRingBuffer
 * Signature: ()Ljava/nio/ByteBuffer;
 */
JNIEXPORT jobject JNICALL Java_com_solorock_amsv_AMSVBridge_getNativeAudioRingBuffer
  (JNIEnv *env, jclass cls);

/*
 * Class:     com_solorock_amsv_AMSVBridge
 * Method:    syncMemoryBarrier
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_com_solorock_amsv_AMSVBridge_syncMemoryBarrier
  (JNIEnv *env, jclass cls);

#ifdef __cplusplus
}
#endif

#endif // AMSV_JNI_BRIDGE_H
