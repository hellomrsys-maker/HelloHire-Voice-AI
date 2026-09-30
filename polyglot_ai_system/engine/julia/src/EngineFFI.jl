# =============================================================================
# engine/julia/src/EngineFFI.jl
# Julia ccall-based FFI bridge to the C++ and Rust engine libraries.
# Exposes Julia functions that wrap the C-linkage exports from engine_core.so
# and engine_rust.so.
# =============================================================================

module EngineFFI

using Libdl

export load_engine_library, load_rust_library,
       engine_create, engine_recruit, engine_process_text,
       engine_is_operational, engine_health_dump, engine_destroy,
       rust_pipeline_create, rust_pipeline_process, rust_pipeline_destroy,
       rust_tokenizer_tokenize, rust_engine_health_check

# =============================================================================
# Library loading
# =============================================================================

# Cached library handles
const _engine_lib  = Ref{Ptr{Nothing}}(C_NULL)
const _rust_lib    = Ref{Ptr{Nothing}}(C_NULL)

"""
    load_engine_library(path::String)

Loads the C++ engine_core shared library from the given path.
"""
function load_engine_library(path::String)
    lib = Libdl.dlopen(path, Libdl.RTLD_LAZY | Libdl.RTLD_GLOBAL)
    _engine_lib[] = lib
    @info "Loaded engine_core library" path=path
    return lib
end

"""
    load_rust_library(path::String)

Loads the Rust engine_rust shared library from the given path.
"""
function load_rust_library(path::String)
    lib = Libdl.dlopen(path, Libdl.RTLD_LAZY | Libdl.RTLD_GLOBAL)
    _rust_lib[] = lib
    @info "Loaded engine_rust library" path=path
    return lib
end

# =============================================================================
# C++ Engine FFI wrappers
# =============================================================================

"""
    engine_create(config_json::String) -> Ptr{Nothing}

Creates an engine instance from a JSON config string.
Returns an opaque pointer (EngineHandle*).
"""
function engine_create(config_json::String) :: Ptr{Nothing}
    config_cstr = Base.unsafe_convert(Cstring, Base.cconvert(Cstring, config_json))
    result = ccall(
        (:engine_create, _engine_lib[]),
        Ptr{Nothing},
        (Cstring,),
        config_json
    )
    return result
end

"""
    engine_recruit(handle::Ptr{Nothing}) -> Bool

Recruits all engine subsystems. Returns true on success.
"""
function engine_recruit(handle::Ptr{Nothing}) :: Bool
    if handle == C_NULL
        error("engine_recruit: null handle")
    end
    result = ccall(
        (:engine_recruit, _engine_lib[]),
        Cint,
        (Ptr{Nothing},),
        handle
    )
    return result == 1
end

"""
    engine_process_text(handle::Ptr{Nothing}, input::String;
                         out_buf_size::Int = 65536) -> String

Processes a text input through the engine. Returns the response text.
"""
function engine_process_text(
    handle::Ptr{Nothing},
    input::String;
    out_buf_size::Int = 65536
) :: String

    if handle == C_NULL
        error("engine_process_text: null handle")
    end

    out_buf = Vector{UInt8}(undef, out_buf_size)
    n_written = ccall(
        (:engine_process_text, _engine_lib[]),
        Cint,
        (Ptr{Nothing}, Cstring, Csize_t, Ptr{UInt8}, Csize_t),
        handle, input, ncodeunits(input), pointer(out_buf), out_buf_size
    )

    if n_written < 0
        error("engine_process_text: C++ call returned error code $n_written")
    end

    return String(out_buf[1:n_written])
end

"""
    engine_is_operational(handle::Ptr{Nothing}) -> Bool

Returns true if the engine is fully operational.
"""
function engine_is_operational(handle::Ptr{Nothing}) :: Bool
    if handle == C_NULL
        return false
    end
    result = ccall(
        (:engine_is_operational, _engine_lib[]),
        Cint,
        (Ptr{Nothing},),
        handle
    )
    return result == 1
end

"""
    engine_health_dump(handle::Ptr{Nothing}) -> String

Returns the engine's JSON health dump.
"""
function engine_health_dump(handle::Ptr{Nothing}) :: String
    if handle == C_NULL
        return "{}"
    end
    ptr = ccall(
        (:engine_health_dump, _engine_lib[]),
        Ptr{UInt8},
        (Ptr{Nothing},),
        handle
    )
    if ptr == Ptr{UInt8}(0)
        return "{}"
    end
    result = unsafe_string(ptr)
    # Free the C-allocated string
    ccall((:engine_free_string, _engine_lib[]), Cvoid, (Ptr{UInt8},), ptr)
    return result
end

"""
    engine_destroy(handle::Ptr{Nothing})

Destroys the engine handle and frees all resources.
"""
function engine_destroy(handle::Ptr{Nothing})
    if handle != C_NULL
        ccall(
            (:engine_destroy, _engine_lib[]),
            Cvoid,
            (Ptr{Nothing},),
            handle
        )
    end
end

# =============================================================================
# Rust Pipeline FFI wrappers
# =============================================================================

"""
    rust_pipeline_create() -> Ptr{Nothing}

Creates a Rust preprocessing pipeline with default config.
"""
function rust_pipeline_create() :: Ptr{Nothing}
    ccall((:rust_pipeline_create, _rust_lib[]), Ptr{Nothing}, ())
end

"""
    rust_pipeline_process(handle::Ptr{Nothing}, input::String) -> String

Processes text through the Rust pipeline. Returns JSON output.
"""
function rust_pipeline_process(handle::Ptr{Nothing}, input::String) :: String
    if handle == C_NULL
        error("rust_pipeline_process: null handle")
    end
    input_bytes = Vector{UInt8}(input)
    ptr = ccall(
        (:rust_pipeline_process, _rust_lib[]),
        Ptr{UInt8},
        (Ptr{Nothing}, Ptr{UInt8}, Cuint),
        handle, pointer(input_bytes), length(input_bytes)
    )
    if ptr == Ptr{UInt8}(0)
        return "{}"
    end
    result = unsafe_string(ptr)
    ccall((:rust_free_string, _rust_lib[]), Cvoid, (Ptr{UInt8},), ptr)
    return result
end

"""
    rust_pipeline_destroy(handle::Ptr{Nothing})
"""
function rust_pipeline_destroy(handle::Ptr{Nothing})
    if handle != C_NULL
        ccall((:rust_pipeline_destroy, _rust_lib[]), Cvoid, (Ptr{Nothing},), handle)
    end
end

"""
    rust_tokenizer_tokenize(handle::Ptr{Nothing}, text::String) -> String

Tokenizes text using the Rust tokenizer. Returns JSON token array.
"""
function rust_tokenizer_tokenize(handle::Ptr{Nothing}, text::String) :: String
    if handle == C_NULL
        error("rust_tokenizer_tokenize: null handle")
    end
    ptr = ccall(
        (:rust_tokenizer_tokenize, _rust_lib[]),
        Ptr{UInt8},
        (Ptr{Nothing}, Cstring),
        handle, text
    )
    if ptr == Ptr{UInt8}(0)
        return "[]"
    end
    result = unsafe_string(ptr)
    ccall((:rust_free_string, _rust_lib[]), Cvoid, (Ptr{UInt8},), ptr)
    return result
end

"""
    rust_engine_health_check() -> Bool

Returns true if the Rust engine module is healthy.
"""
function rust_engine_health_check() :: Bool
    if _rust_lib[] == C_NULL
        @warn "Rust library not loaded — call load_rust_library() first"
        return false
    end
    result = ccall((:rust_engine_health_check, _rust_lib[]), Cint, ())
    return result == 1
end

end # module EngineFFI
