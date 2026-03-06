"""
Tiny Python wrapper for the LIS (Lucas Index System) PoC library.

Provides simple, batch-oriented helpers you can drop into existing pipelines
to prune candidates before Miller–Rabin and measure MR-call reduction.
"""
from __future__ import annotations

import ctypes as C
import os
from typing import Iterable, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))  # repo root
LIS_DIR = os.path.join(REPO, "src", "c", "lis")
LIB_DIR = os.path.join(LIS_DIR, "lib")


def build_lis_if_needed() -> None:
    # Try to build; Makefile will create necessary directories.
    os.system(f"make -C {LIS_DIR} all > /dev/null 2>&1")


class _LISLib:
    def __init__(self) -> None:
        build_lis_if_needed()
        if os.name == "posix" and hasattr(os, "uname") and os.uname().sysname == "Darwin":
            libname = os.path.join(LIB_DIR, "liblis.dylib")
        else:
            libname = os.path.join(LIB_DIR, "liblis.so")
        self.lib = C.CDLL(libname)

        class _Cfg(C.Structure):
            _fields_ = [("P", C.c_int64), ("Q", C.c_int64)]

        self.Cfg = _Cfg
        self.cfg = _Cfg()
        self.lib.lis_init_default(C.byref(self.cfg))

        # Prototypes
        self.lib.lis_passes_wheel210.argtypes = [C.c_uint64]
        self.lib.lis_passes_wheel210.restype = C.c_int
        self.lib.lis_filter.argtypes = [C.c_uint64, C.POINTER(_Cfg)]
        self.lib.lis_filter.restype = C.c_int
        self.lib.lis_filter_batch.argtypes = [C.POINTER(C.c_uint64), C.c_size_t, C.POINTER(C.c_uint8), C.POINTER(_Cfg)]
        self.lib.lis_filter_batch.restype = None

    def wheel210(self, n: int) -> bool:
        return bool(self.lib.lis_passes_wheel210(C.c_uint64(n)))

    def filter_batch(self, nums: List[int]) -> List[int]:
        """Return a mask (0/1) for nums indicating which pass LIS (wheel-210 + Lucas)."""
        k = len(nums)
        buf_in = (C.c_uint64 * k)(*nums)
        buf_out = (C.c_uint8 * k)()
        self.lib.lis_filter_batch(buf_in, k, buf_out, C.byref(self.cfg))
        return [int(buf_out[i]) for i in range(k)]


_LIB_SINGLETON: _LISLib | None = None


def get_lis() -> _LISLib:
    global _LIB_SINGLETON
    if _LIB_SINGLETON is None:
        _LIB_SINGLETON = _LISLib()
    return _LIB_SINGLETON


def wheel210(n: int) -> bool:
    return get_lis().wheel210(n)


def prune_with_lis(iterable: Iterable[int], batch_size: int = 8192) -> Iterable[int]:
    """Yield only numbers that pass LIS (wheel-210 + Lucas)."""
    lis = get_lis()
    batch: List[int] = []
    for n in iterable:
        batch.append(int(n))
        if len(batch) >= batch_size:
            mask = lis.filter_batch(batch)
            for i, keep in enumerate(mask):
                if keep:
                    yield batch[i]
            batch.clear()
    if batch:
        mask = lis.filter_batch(batch)
        for i, keep in enumerate(mask):
            if keep:
                yield batch[i]


def reduction_vs_wheel210(iterable: Iterable[int], batch_size: int = 8192) -> Tuple[int, int, float]:
    """Return (baseline_wheel210, after_lis, reduction) for the given iterable."""
    lis = get_lis()
    baseline = 0
    after = 0
    batch: List[int] = []
    for n in iterable:
        n = int(n)
        if lis.wheel210(n):
            baseline += 1
        batch.append(n)
        if len(batch) >= batch_size:
            mask = lis.filter_batch(batch)
            after += sum(mask)
            batch.clear()
    if batch:
        mask = lis.filter_batch(batch)
        after += sum(mask)
    reduction = 0.0 if baseline == 0 else (1.0 - after / baseline)
    return baseline, after, reduction
