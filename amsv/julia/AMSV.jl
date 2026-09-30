"""
AMSV.jl — Advanced Multi-language Shared Memory Interface for Julia.
Direct memory access to the 64-byte Atomic Memory State Vector and Audio Buffer.
"""
module AMSV

export AtomicStateVectorView, get_phoneme_state, set_phoneme_state,
       get_cognitive_score, set_cognitive_score, get_examination_theta,
       set_examination_theta, sync_memory_barrier

struct AtomicStateVectorView
    ptr::Ptr{UInt8}

    function AtomicStateVectorView(raw_ptr::Ptr{UInt8})
        @assert raw_ptr != C_NULL "AMSV pointer cannot be null"
        @assert UInt(raw_ptr) % 64 == 0 "AMSV pointer must be 64-byte aligned"
        return new(raw_ptr)
    end
end

"""Retrieve phoneme state from byte offset 0x00."""
function get_phoneme_state(v::AtomicStateVectorView)::UInt64
    return unsafe_load(Ptr{UInt64}(v.ptr + 0))
end

"""Store phoneme state to byte offset 0x00."""
function set_phoneme_state(v::AtomicStateVectorView, state::UInt64)
    unsafe_store!(Ptr{UInt64}(v.ptr + 0), state)
end

"""Retrieve prosody state from byte offset 0x08."""
function get_prosody_state(v::AtomicStateVectorView)::UInt64
    return unsafe_load(Ptr{UInt64}(v.ptr + 8))
end

"""Store prosody state to byte offset 0x08."""
function set_prosody_state(v::AtomicStateVectorView, state::UInt64)
    unsafe_store!(Ptr{UInt64}(v.ptr + 8), state)
end

"""Retrieve one of the 8 cognitive capability scores (0 to 7) as Float32."""
function get_cognitive_score(v::AtomicStateVectorView, idx::Int)::Float32
    @assert 0 <= idx <= 7 "Capability index must be between 0 and 7"
    offset = 16 + idx * 2
    raw_val = unsafe_load(Ptr{UInt16}(v.ptr + offset))
    return Float32(raw_val) / Float32(65535.0)
end

"""Set one of the 8 cognitive capability scores (0 to 7)."""
function set_cognitive_score(v::AtomicStateVectorView, idx::Int, score::Float32)
    @assert 0 <= idx <= 7 "Capability index must be between 0 and 7"
    offset = 16 + idx * 2
    clamped = clamp(score, 0.0f0, 1.0f0)
    fixed_val = round(UInt16, clamped * 65535.0f0)
    unsafe_store!(Ptr{UInt16}(v.ptr + offset), fixed_val)
end

"""Retrieve examination IRT ability theta (Float32) from byte offset 0x28."""
function get_examination_theta(v::AtomicStateVectorView)::Float32
    return unsafe_load(Ptr{Float32}(v.ptr + 40))
end

"""Store examination IRT ability theta (Float32) to byte offset 0x28."""
function set_examination_theta(v::AtomicStateVectorView, theta::Float32)
    unsafe_store!(Ptr{Float32}(v.ptr + 40), theta)
end

"""Execute sequential consistency memory barrier."""
function sync_memory_barrier()
    ccall(:jl_fence, Cvoid, ())
end

end # module AMSV
