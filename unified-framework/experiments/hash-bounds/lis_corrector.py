#!/usr/bin/env python3
"""
ctypes wrapper for LIS Corrector (Z5D seed + LIS + MR) — PoC
"""
from __future__ import annotations

import ctypes as C
import os
import subprocess
from typing import Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LISC_DIR = os.path.join(REPO, "src", "c", "lis_corrector")
LIS_DIR = os.path.join(REPO, "src", "c", "lis")
Z5D_DIR = os.path.join(REPO, "src", "c")

_BUILT = False

def _lib_paths():
    if os.name == "posix" and hasattr(os, "uname") and os.uname().sysname == "Darwin":
        lc = os.path.join(LISC_DIR, "lib", "liblis_corrector.dylib")
        ll = os.path.join(LIS_DIR, "lib", "liblis.dylib")
    else:
        lc = os.path.join(LISC_DIR, "lib", "liblis_corrector.so")
        ll = os.path.join(LIS_DIR, "lib", "liblis.so")
    return lc, ll


def _build_all() -> None:
    global _BUILT
    if _BUILT:
        return
    lc, ll = _lib_paths()
    # If both libs exist, skip
    if os.path.exists(lc) and os.path.exists(ll):
        _BUILT = True
        return
    # Build quietly
    subprocess.run(["make", "-C", Z5D_DIR, "shared"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r1 = subprocess.run(["make", "-C", LIS_DIR, "all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r2 = subprocess.run(["make", "-C", LISC_DIR, "all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not (os.path.exists(ll) and os.path.exists(lc)) or r1.returncode not in (0,) or r2.returncode not in (0,):
        raise RuntimeError("LIS build failed; run 'make -C src/c/lis' and 'make -C src/c/lis_corrector'")
    _BUILT = True


def lis_correct_nth_prime(n: int, window: int = 100000) -> Tuple[int, int, int]:
    # Attempt build if missing (single attempt, raises if fails)
    _build_all()

    if os.name == "posix" and hasattr(os, "uname") and os.uname().sysname == "Darwin":
        libname = os.path.join(LISC_DIR, "lib", "liblis_corrector.dylib")
    else:
        libname = os.path.join(LISC_DIR, "lib", "liblis_corrector.so")

    if not os.path.exists(libname):
        raise RuntimeError("liblis_corrector not found. Please run: make -C src/c/lis && make -C src/c/lis_corrector")

    lib = C.CDLL(libname)
    lib.lis_correct_nth_prime.argtypes = [C.c_uint64, C.c_uint64,
                                          C.POINTER(C.c_uint64), C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    lib.lis_correct_nth_prime.restype = C.c_int

    out_prime = C.c_uint64(0)
    out_mr = C.c_uint64(0)
    out_base = C.c_uint64(0)
    rc = lib.lis_correct_nth_prime(C.c_uint64(n), C.c_uint64(window), C.byref(out_prime), C.byref(out_mr), C.byref(out_base))
    if rc != 0:
        raise RuntimeError(f"lis_correct_nth_prime failed (rc={rc}) for n={n}")
    return int(out_prime.value), int(out_mr.value), int(out_base.value)
