// =============================================================================
// ffi/java_cpp/EngineJNI.cpp
// JNI implementation for the Java EngineLibraryBridge.
// Implements the native methods declared in EngineLibraryBridge.java.
// =============================================================================

#include <jni.h>
#include <string>
#include <cstring>
#include <memory>
#include <unordered_map>
#include <mutex>

#include "EngineCore.h"

// =============================================================================
// Handle registry — maps Java-visible long IDs to C++ EngineCore instances.
// Needed because JNI passes primitives (jlong) across the boundary.
// =============================================================================

static std::unordered_map<jlong, engine::EngineCore*> g_handle_map;
static std::mutex g_map_mutex;
static jlong g_next_id = 1;

static jlong registerHandle(engine::EngineCore* engine) {
    std::lock_guard<std::mutex> lock(g_map_mutex);
    jlong id = g_next_id++;
    g_handle_map[id] = engine;
    return id;
}

static engine::EngineCore* lookupHandle(jlong id) {
    std::lock_guard<std::mutex> lock(g_map_mutex);
    auto it = g_handle_map.find(id);
    return (it != g_handle_map.end()) ? it->second : nullptr;
}

static void removeHandle(jlong id) {
    std::lock_guard<std::mutex> lock(g_map_mutex);
    g_handle_map.erase(id);
}

// =============================================================================
// Helper: convert jstring to std::string
// =============================================================================

static std::string jstringToStd(JNIEnv* env, jstring jstr) {
    if (!jstr) return "";
    const char* chars = env->GetStringUTFChars(jstr, nullptr);
    std::string result(chars);
    env->ReleaseStringUTFChars(jstr, chars);
    return result;
}

static jstring stdToJstring(JNIEnv* env, const std::string& str) {
    return env->NewStringUTF(str.c_str());
}

// =============================================================================
// JNI implementations — matches the native method signatures in
// ai.engine.infra.EngineLibraryBridge
// =============================================================================

extern "C" {

/**
 * long nativeCreateEngine(String configJson)
 */
JNIEXPORT jlong JNICALL
Java_ai_engine_infra_EngineLibraryBridge_nativeCreateEngine(
    JNIEnv* env, jobject /*this*/, jstring configJson)
{
    try {
        std::string json = jstringToStd(env, configJson);

        engine::EngineConfig config;
        config.engine_id        = "jni_engine";
        config.engine_version   = "1.0.0";
        config.default_language = "en";
        config.thread_pool_size = 4;
        config.enable_gpu       = false;
        config.attention_heads  = 8;
        config.attention_dim    = 512;
        config.max_sequence_length = 512;
        config.episodic_memory_slots = 1024;
        config.semantic_memory_slots = 8192;
        config.working_memory_bytes  = 256 * 1024 * 1024;

        auto* eng = new engine::EngineCore(std::move(config));
        return registerHandle(eng);

    } catch (const std::exception& e) {
        env->ThrowNew(env->FindClass("java/lang/RuntimeException"), e.what());
        return 0L;
    }
}

/**
 * int nativeRecruitSubsystems(long handle)
 */
JNIEXPORT jint JNICALL
Java_ai_engine_infra_EngineLibraryBridge_nativeRecruitSubsystems(
    JNIEnv* env, jobject /*this*/, jlong handle)
{
    engine::EngineCore* eng = lookupHandle(handle);
    if (!eng) {
        env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),
                      "Engine handle is invalid");
        return 0;
    }
    try {
        return eng->recruitAllSubsystems() ? 1 : 0;
    } catch (const std::exception& e) {
        env->ThrowNew(env->FindClass("java/lang/RuntimeException"), e.what());
        return 0;
    }
}

/**
 * String nativeProcessText(long handle, String input, int depth, int modality)
 */
JNIEXPORT jstring JNICALL
Java_ai_engine_infra_EngineLibraryBridge_nativeProcessText(
    JNIEnv* env, jobject /*this*/,
    jlong handle, jstring input, jint depth, jint modality)
{
    engine::EngineCore* eng = lookupHandle(handle);
    if (!eng) {
        env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),
                      "Engine handle is invalid");
        return env->NewStringUTF("");
    }
    try {
        std::string text = jstringToStd(env, input);

        engine::ReasoningDepth rdepth =
            static_cast<engine::ReasoningDepth>(
                std::clamp(static_cast<int>(depth), 0, 3));

        engine::OutputModality rmodality =
            static_cast<engine::OutputModality>(
                std::clamp(static_cast<int>(modality), 0, 3));

        auto response = eng->processText(text, rmodality, rdepth);
        return stdToJstring(env, response.text);

    } catch (const std::exception& e) {
        env->ThrowNew(env->FindClass("java/lang/RuntimeException"), e.what());
        return env->NewStringUTF("");
    }
}

/**
 * int nativeIsOperational(long handle)
 */
JNIEXPORT jint JNICALL
Java_ai_engine_infra_EngineLibraryBridge_nativeIsOperational(
    JNIEnv* /*env*/, jobject /*this*/, jlong handle)
{
    engine::EngineCore* eng = lookupHandle(handle);
    if (!eng) return 0;
    return eng->isOperational() ? 1 : 0;
}

/**
 * String nativeHealthDump(long handle)
 */
JNIEXPORT jstring JNICALL
Java_ai_engine_infra_EngineLibraryBridge_nativeHealthDump(
    JNIEnv* env, jobject /*this*/, jlong handle)
{
    engine::EngineCore* eng = lookupHandle(handle);
    if (!eng) return env->NewStringUTF("{}");
    try {
        return stdToJstring(env, eng->healthDump());
    } catch (...) {
        return env->NewStringUTF("{}");
    }
}

/**
 * void nativeDestroyEngine(long handle)
 */
JNIEXPORT void JNICALL
Java_ai_engine_infra_EngineLibraryBridge_nativeDestroyEngine(
    JNIEnv* /*env*/, jobject /*this*/, jlong handle)
{
    engine::EngineCore* eng = lookupHandle(handle);
    if (eng) {
        eng->shutdown();
        delete eng;
        removeHandle(handle);
    }
}

} // extern "C"
