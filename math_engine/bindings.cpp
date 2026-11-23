#include <pybind11/pybind11.h>
#include "black_scholes.h"

namespace py = pybind11;

PYBIND11_MODULE(pricing_engine, m) {
    m.doc() = "High-performance C++ Black-Scholes pricing and Greeks engine";

    py::enum_<pricing::OptionType>(m, "OptionType")
        .value("Call", pricing::OptionType::Call)
        .value("Put", pricing::OptionType::Put)
        .export_values();

    py::class_<pricing::OptionMetrics>(m, "OptionMetrics")
        .def_readonly("price", &pricing::OptionMetrics::price)
        .def_readonly("delta", &pricing::OptionMetrics::delta)
        .def_readonly("gamma", &pricing::OptionMetrics::gamma)
        .def_readonly("vega",  &pricing::OptionMetrics::vega)
        .def_readonly("theta", &pricing::OptionMetrics::theta)
        .def_readonly("rho",   &pricing::OptionMetrics::rho)
        .def("__repr__", [](const pricing::OptionMetrics &o) {
            return "<OptionMetrics price=" + std::to_string(o.price) +
                   " delta=" + std::to_string(o.delta) +
                   " gamma=" + std::to_string(o.gamma) + ">";
        });

    m.def(
        "calculate_black_scholes",
        &pricing::calculate_black_scholes,
        "Compute Black-Scholes price and Greeks in a single pass",
        py::arg("S"),
        py::arg("K"),
        py::arg("T"),
        py::arg("r"),
        py::arg("sigma"),
        py::arg("type") = pricing::OptionType::Call,
        py::call_guard<py::gil_scoped_release>()
    );
}