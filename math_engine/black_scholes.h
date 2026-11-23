#pragma once

namespace pricing {

enum class OptionType {
    Call,
    Put
};

struct OptionMetrics {
    double price;
    double delta;
    double gamma;
    double vega;
    double theta;
    double rho;
};

OptionMetrics calculate_black_scholes(
    double S,
    double K,
    double T,
    double r,
    double sigma,
    OptionType type
);

} // namespace pricing