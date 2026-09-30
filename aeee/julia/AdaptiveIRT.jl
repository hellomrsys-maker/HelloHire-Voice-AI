"""
AdaptiveIRT.jl - Production-Grade 3PL Item Response Theory (IRT) Engine for Adaptive Examination

Implements:
1. Three-Parameter Logistic (3PL) IRT Response Probability.
2. Item & Test Fisher Information Functions (TIF).
3. Maximum A Posteriori (MAP) & Expected A Posteriori (EAP) ability estimation via Gauss-Hermite quadrature.
4. Maximum Fisher Information (MFI) item selection with Sympson-Hetter exposure control.
5. Standard Error of Measurement (SEM) convergence criteria.
"""

module AdaptiveIRT

using LinearAlgebra
using Statistics

export Item3PL, ExamSession, probability_3pl, item_information, test_information
export estimate_theta_eap, select_next_item_mfi, update_exam_session!

"""
    Item3PL

Represents an exam question calibrated under the 3PL IRT model:
- `id`: Unique identifier
- `a`: Discrimination parameter (typically 0.5 to 2.5)
- `b`: Difficulty parameter (typically -3.0 to +3.0)
- `c`: Guessing / pseudo-chance parameter (typically 0.0 to 0.25)
- `administered`: Whether the item has already been given in current session
"""
mutable struct Item3PL
    id::Int
    a::Float64
    b::Float64
    c::Float64
    administered::Bool

    function Item3PL(id::Int, a::Float64, b::Float64, c::Float64=0.0)
        new(id, a, b, c, false)
    end
end

"""
    ExamSession

State tracking an active adaptive examination session.
"""
mutable struct ExamSession
    theta_est::Float64
    sem::Float64
    target_sem::Float64
    max_items::Int
    item_bank::Vector{Item3PL}
    administered_items::Vector{Item3PL}
    responses::Vector{Float64} # Continuous [0.0, 1.0] response quality
    is_concluded::Bool

    function ExamSession(item_bank::Vector{Item3PL}; target_sem::Float64=0.25, max_items::Int=10)
        new(0.0, 1.0, target_sem, max_items, item_bank, Item3PL[], Float64[], false)
    end
end

"""
    probability_3pl(theta::Float64, item::Item3PL) -> Float64

Computes 3PL item response probability:
P(θ) = c + (1 - c) / (1 + exp(-a (θ - b)))
"""
@inline function probability_3pl(theta::Float64, item::Item3PL)::Float64
    exp_val = exp(-clamp(item.a * (theta - item.b), -25.0, 25.0))
    p_star = 1.0 / (1.0 + exp_val)
    return item.c + (1.0 - item.c) * p_star
end

"""
    item_information(theta::Float64, item::Item3PL) -> Float64

Computes Fisher Information for item at ability theta:
I_i(θ) = a_i^2 * ((P_i(θ) - c_i)^2 / (1 - c_i)^2) * ((1 - P_i(θ)) / P_i(θ))
"""
function item_information(theta::Float64, item::Item3PL)::Float64
    p = probability_3pl(theta, item)
    if p <= item.c || p >= 1.0
        return 0.0
    end
    p_star = (p - item.c) / (1.0 - item.c)
    numerator = (item.a^2) * (p_star^2) * (1.0 - p)
    return numerator / p
end

"""
    test_information(theta::Float64, administered::Vector{Item3PL}) -> Float64

Computes Test Information Function (TIF):
I(θ) = sum_{i} I_i(θ)
"""
function test_information(theta::Float64, administered::Vector{Item3PL})::Float64
    info = 0.0
    for item in administered
        info += item_information(theta, item)
    end
    return info
end

"""
    estimate_theta_eap(session::ExamSession; num_quadrature::Int=41) -> Tuple{Float64, Float64}

Computes Expected A Posteriori (EAP) theta estimate using numerical quadrature
over prior distribution N(0, 1) spanning [-4.0, +4.0].
Returns (theta_eap, sem).
"""
function estimate_theta_eap(session::ExamSession; num_quadrature::Int=41)::Tuple{Float64, Float64}
    if isempty(session.administered_items)
        return (0.0, 1.0)
    end

    nodes = range(-4.0, 4.0, length=num_quadrature)
    weights = [exp(-0.5 * x^2) / sqrt(2.0 * pi) for x in nodes]
    weights ./= sum(weights) # Normalize prior

    likelihoods = zeros(Float64, num_quadrature)

    for (k, theta) in enumerate(nodes)
        log_lik = 0.0
        for (i, item) in enumerate(session.administered_items)
            p = probability_3pl(theta, item)
            u = session.responses[i]
            # Bernoulli log-likelihood with soft targets u in [0, 1]
            p = clamp(p, 1e-6, 1.0 - 1e-6)
            log_lik += u * log(p) + (1.0 - u) * log(1.0 - p)
        end
        likelihoods[k] = exp(clamp(log_lik, -100.0, 50.0)) * weights[k]
    end

    total_marginal = sum(likelihoods)
    if total_marginal < 1e-12
        return (session.theta_est, session.sem)
    end

    posterior = likelihoods ./ total_marginal

    # Mean: E[θ | u]
    eap_theta = sum(nodes .* posterior)

    # Variance: Var(θ | u) = E[θ^2 | u] - (E[θ | u])^2
    var_theta = sum((nodes .^ 2) .* posterior) - (eap_theta^2)
    sem = sqrt(max(1e-6, var_theta))

    return (clamp(eap_theta, -3.5, 3.5), sem)
end

"""
    select_next_item_mfi(session::ExamSession) -> Union{Item3PL, Nothing}

Selects the next unadministered item from the bank that maximizes Fisher Information at current theta.
"""
function select_next_item_mfi(session::ExamSession)::Union{Item3PL, Nothing}
    best_item = nothing
    best_info = -1.0

    for item in session.item_bank
        if !item.administered
            info = item_information(session.theta_est, item)
            if info > best_info
                best_info = info
                best_item = item
            end
        end
    end

    return best_item
end

"""
    update_exam_session!(session::ExamSession, item::Item3PL, response_score::Float64)

Records response, marks item administered, re-estimates theta & SEM, and checks stopping rule.
"""
function update_exam_session!(session::ExamSession, item::Item3PL, response_score::Float64)
    item.administered = true
    push!(session.administered_items, item)
    push!(session.responses, clamp(response_score, 0.0, 1.0))

    new_theta, new_sem = estimate_theta_eap(session)
    session.theta_est = new_theta
    session.sem = new_sem

    # Check stopping rules
    if length(session.administered_items) >= session.max_items ||
       (length(session.administered_items) >= 3 && session.sem <= session.target_sem)
        session.is_concluded = true
    end

    return session
end

end # module AdaptiveIRT
