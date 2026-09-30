// =============================================================================
// ffi/python_cpp/engine_pybind.cpp
// pybind11 bridge: exposes the C++ EngineCore to Python.
// Provides a clean Python API matching the engine_client.py stub interface.
// =============================================================================

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

// Include the engine headers
#include "EngineCore.h"
#include "VocalInputProcessor.h"

namespace py = pybind11;
using namespace engine;

// =============================================================================
// Python module definition
// =============================================================================

PYBIND11_MODULE(engine_core_py, m) {
    m.doc() = R"doc(
        engine_core_py — Python bindings for the C++ Verbal Communication Engine.

        Provides direct Python access to the EngineCore class and all related
        types, bypassing the ctypes FFI layer for higher performance and type safety.
    )doc";

    // =========================================================================
    // Enumerations
    // =========================================================================

    py::enum_<EngineStatus>(m, "EngineStatus")
        .value("UNINITIALIZED", EngineStatus::UNINITIALIZED)
        .value("RECRUITING",    EngineStatus::RECRUITING)
        .value("OPERATIONAL",   EngineStatus::OPERATIONAL)
        .value("PROCESSING",    EngineStatus::PROCESSING)
        .value("SUSPENDED",     EngineStatus::SUSPENDED)
        .value("ERROR_STATE",   EngineStatus::ERROR_STATE)
        .value("SHUTDOWN",      EngineStatus::SHUTDOWN)
        .export_values();

    py::enum_<InputModality>(m, "InputModality")
        .value("TEXT",        InputModality::TEXT)
        .value("SPEECH_PCM",  InputModality::SPEECH_PCM)
        .value("SPEECH_OPUS", InputModality::SPEECH_OPUS)
        .export_values();

    py::enum_<OutputModality>(m, "OutputModality")
        .value("TEXT",        OutputModality::TEXT)
        .value("SPEECH_PCM",  OutputModality::SPEECH_PCM)
        .value("SPEECH_OPUS", OutputModality::SPEECH_OPUS)
        .value("STRUCTURED",  OutputModality::STRUCTURED)
        .export_values();

    py::enum_<ReasoningDepth>(m, "ReasoningDepth")
        .value("SHALLOW",  ReasoningDepth::SHALLOW)
        .value("MODERATE", ReasoningDepth::MODERATE)
        .value("DEEP",     ReasoningDepth::DEEP)
        .value("EXTENDED", ReasoningDepth::EXTENDED)
        .export_values();

    py::enum_<RegisterType>(m, "RegisterType")
        .value("FORMAL",         RegisterType::FORMAL)
        .value("NEUTRAL",        RegisterType::NEUTRAL)
        .value("INFORMAL",       RegisterType::INFORMAL)
        .value("TECHNICAL",      RegisterType::TECHNICAL)
        .value("CREATIVE",       RegisterType::CREATIVE)
        .value("CHILD_DIRECTED", RegisterType::CHILD_DIRECTED)
        .export_values();

    // =========================================================================
    // Token
    // =========================================================================

    py::class_<Token>(m, "Token")
        .def(py::init<>())
        .def_readwrite("surface",    &Token::surface)
        .def_readwrite("normalized", &Token::normalized)
        .def_readwrite("lemma",      &Token::lemma)
        .def_readwrite("pos_tag",    &Token::pos_tag)
        .def_readwrite("dep_label",  &Token::dep_label)
        .def_readwrite("position",   &Token::position)
        .def_readwrite("char_start", &Token::char_start)
        .def_readwrite("char_end",   &Token::char_end)
        .def_readwrite("confidence", &Token::confidence)
        .def_readwrite("is_special", &Token::is_special)
        .def("__repr__", [](const Token& t) {
            return "<Token surface='" + t.surface + "' pos='" + t.pos_tag + "'>";
        });

    // =========================================================================
    // Intent
    // =========================================================================

    py::class_<Intent>(m, "Intent")
        .def(py::init<>())
        .def_readwrite("name",       &Intent::name)
        .def_readwrite("confidence", &Intent::confidence)
        .def_readwrite("slots",      &Intent::slots)
        .def("__repr__", [](const Intent& i) {
            return "<Intent name='" + i.name + "' conf=" + std::to_string(i.confidence) + ">";
        });

    // =========================================================================
    // MeaningFrame
    // =========================================================================

    py::class_<MeaningFrame>(m, "MeaningFrame")
        .def(py::init<>())
        .def_readwrite("primary_intent",     &MeaningFrame::primary_intent)
        .def_readwrite("secondary_intents",  &MeaningFrame::secondary_intents)
        .def_readwrite("literal_meaning",    &MeaningFrame::literal_meaning)
        .def_readwrite("natural_meaning",    &MeaningFrame::natural_meaning)
        .def_readwrite("detected_register",  &MeaningFrame::detected_register)
        .def_readwrite("sentiment",          &MeaningFrame::sentiment)
        .def_readwrite("certainty",          &MeaningFrame::certainty);

    // =========================================================================
    // EngineResponse
    // =========================================================================

    py::class_<EngineResponse>(m, "EngineResponse")
        .def(py::init<>())
        .def_readwrite("text",            &EngineResponse::text)
        .def_readwrite("modality",        &EngineResponse::modality)
        .def_readwrite("confidence",      &EngineResponse::confidence)
        .def_readwrite("reasoning_trace", &EngineResponse::reasoning_trace)
        .def_readwrite("latency",         &EngineResponse::latency)
        .def("__repr__", [](const EngineResponse& r) {
            return "<EngineResponse text='" + r.text.substr(0, 60) + "...'>";
        });

    // =========================================================================
    // EngineConfig
    // =========================================================================

    py::class_<EngineConfig>(m, "EngineConfig")
        .def(py::init<>())
        .def_readwrite("engine_id",             &EngineConfig::engine_id)
        .def_readwrite("engine_version",        &EngineConfig::engine_version)
        .def_readwrite("default_language",      &EngineConfig::default_language)
        .def_readwrite("supported_languages",   &EngineConfig::supported_languages)
        .def_readwrite("thread_pool_size",      &EngineConfig::thread_pool_size)
        .def_readwrite("max_batch_size",        &EngineConfig::max_batch_size)
        .def_readwrite("max_sequence_length",   &EngineConfig::max_sequence_length)
        .def_readwrite("enable_gpu",            &EngineConfig::enable_gpu)
        .def_readwrite("attention_heads",       &EngineConfig::attention_heads)
        .def_readwrite("attention_dim",         &EngineConfig::attention_dim)
        .def_readwrite("enable_safety_filter",  &EngineConfig::enable_safety_filter)
        .def_readwrite("enable_privacy_guard",  &EngineConfig::enable_privacy_guard);

    // =========================================================================
    // EngineCore
    // =========================================================================

    py::class_<EngineCore>(m, "EngineCore")
        .def(py::init<EngineConfig>(),
             py::arg("config"),
             "Construct an EngineCore with the given configuration.")

        .def("recruit_all_subsystems", &EngineCore::recruitAllSubsystems,
             "Recruits all engine subsystems in dependency order.\n"
             "Must be called before process_text().")

        .def("recruit_subsystem", &EngineCore::recruitSubsystem,
             py::arg("subsystem_name"),
             "Recruits a single named subsystem.")

        .def("is_operational", &EngineCore::isOperational,
             "Returns True if all subsystems are recruited and ready.")

        .def("process_text",
             [](EngineCore& eng, const std::string& input,
                OutputModality modality, ReasoningDepth depth) {
                 return eng.processText(input, modality, depth);
             },
             py::arg("input"),
             py::arg("modality") = OutputModality::TEXT,
             py::arg("depth")    = ReasoningDepth::MODERATE,
             "Processes a text input through the full engine pipeline.\n"
             "Returns an EngineResponse with the realized response text.")

        .def("status",       &EngineCore::status,
             "Returns current EngineStatus.")

        .def("status_report", &EngineCore::statusReport,
             "Returns a status summary string.")

        .def("health_dump", &EngineCore::healthDump,
             "Returns a JSON-serialized health dump.")

        .def("shutdown", &EngineCore::shutdown,
             "Gracefully shuts down all subsystems.")

        .def("__enter__", [](EngineCore& eng) -> EngineCore& {
            return eng;
        })
        .def("__exit__", [](EngineCore& eng, py::object, py::object, py::object) {
            eng.shutdown();
        });

    // =========================================================================
    // EngineFactory
    // =========================================================================

    py::class_<EngineFactory>(m, "EngineFactory")
        .def_static("create_from_config", &EngineFactory::createFromConfig,
                    py::arg("config"),
                    "Creates and recruits an engine from an EngineConfig.")
        .def_static("create_from_training_file",
                    &EngineFactory::createFromTrainingFile,
                    py::arg("training_file_path"),
                    "Creates an engine from a canonical YAML training file.");

    // =========================================================================
    // Module-level convenience function
    // =========================================================================

    m.def("create_default_engine", []() {
        EngineConfig config;
        config.engine_id      = "default_engine";
        config.engine_version = "1.0.0";
        config.default_language = "en";
        config.thread_pool_size = 4;
        config.enable_gpu = false;
        config.attention_heads = 8;
        config.attention_dim = 512;
        return EngineFactory::createFromConfig(std::move(config));
    }, "Creates a default-configured EngineCore (no GPU, small config).");

    m.attr("__version__") = "1.0.0";
}
