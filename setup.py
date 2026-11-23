import sys
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

extra_compile_args = ["/O2"] if sys.platform == "win32" else ["-O3", "-march=native"]

ext_modules = [
    Pybind11Extension(
        "pricing_engine",
        sources=[
            "math_engine/black_scholes.cpp",
            "math_engine/bindings.cpp",
        ],
        cxx_std=17,
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name="pricing_engine",
    version="0.1.0",
    description="C++ Black-Scholes Engine for Reactive Options DAG",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)