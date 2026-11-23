#include "black_scholes.h"
#include <cmath>
#include <algorithm>

namespace pricing {

namespace {
    constexpr double INV_SQRT_2PI = 0.39894228040143267794; // 1 / sqrt(2 * pi)
    constexpr double INV_SQRT_2   = 0.70710678118654752440; // 1 / sqrt(2)

    inline double norm_pdf(double x) {
        return INV_SQRT_2PI * std::exp(-0.5 * x * x);
    }

    inline double norm_cdf(double x) {
        return 0.5 * std::erfc(-x * INV_SQRT_2);
    }
}

OptionMetrics calculate_black_scholes(
    double S,
    double K,
    double T,
    double r,
    double sigma,
    OptionType type
) {
    // Handle expiration or zero-volatility edge cases safely
    if (T <= 0.0 || sigma <= 0.0) {
        double intrinsic = (type == OptionType::Call)
            ? std::max(0.0, S - K)
            : std::max(0.0, K - S);
        double delta = 0.0;
        if (type == OptionType::Call && S > K) delta = 1.0;
        if (type == OptionType::Put  && S < K) delta = -1.0;
        return {intrinsic, delta, 0.0, 0.0, 0.0, 0.0};
    }

    const double sqrt_T   = std::sqrt(T);
    const double vol_sqrt = sigma * sqrt_T;
    const double d1       = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / vol_sqrt;
    const double d2       = d1 - vol_sqrt;

    const double pdf_d1   = norm_pdf(d1);
    const double cdf_d1   = norm_cdf(d1);
    const double cdf_d2   = norm_cdf(d2);
    const double discount = std::exp(-r * T);

    OptionMetrics res{};

    // Gamma and Vega are identical for Calls and Puts
    res.gamma = pdf_d1 / (S * vol_sqrt);
    res.vega  = (S * pdf_d1 * sqrt_T) / 100;

    if (type == OptionType::Call) {
        res.price = S * cdf_d1 - K * discount * cdf_d2;
        res.delta = cdf_d1;
        res.theta = (-(S * pdf_d1 * sigma) / (2.0 * sqrt_T) - r * K * discount * cdf_d2) / 365.0;
        res.rho   = (K * T * discount * cdf_d2) / 100.0 ;
    } else {
        const double cdf_neg_d1 = 1.0 - cdf_d1;
        const double cdf_neg_d2 = 1.0 - cdf_d2;

        res.price = K * discount * cdf_neg_d2 - S * cdf_neg_d1;
        res.delta = cdf_d1 - 1.0;
        res.theta = (-(S * pdf_d1 * sigma) / (2.0 * sqrt_T) + r * K * discount * cdf_neg_d2) / 365.0;
        res.rho   = (-K * T * discount * cdf_neg_d2) / 100.0;
    }

    return res;
}

} // namespace pricing