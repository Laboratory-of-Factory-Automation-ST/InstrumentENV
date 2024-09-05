# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:45:09 2024

@author: marek novotny
"""
from src.instrument_drivers.generic import ContextGuard
from src.product_scripts import ips8200hq

"""
Usage example:
    ips8200hq.ips8200hq_out16a1_pgood_convex_ramp()
Please keep your custom main code on your private branches
"""

RUN_MEASUREMENT = 0

with ContextGuard(ContextGuard.SkipContext()) as ctx_guard:
    if RUN_MEASUREMENT != 1:
        raise ctx_guard.Skip()
    ips8200hq.ips8200hq_out16a1_pgood_convex_ramp(5, 10)

with ContextGuard(ContextGuard.SkipContext()) as ctx_guard:
    if RUN_MEASUREMENT != 2:
        raise ctx_guard.Skip()
    ips8200hq.ips8200hq_out16a1_pgood_concave_ramp(5, 10)

with ContextGuard(ContextGuard.SkipContext()) as ctx_guard:
    if RUN_MEASUREMENT != 3:
        raise ctx_guard.Skip()
    ips8200hq.ips8200hq_out16a1_uvlo_convex_ramp(5, 10)

with ContextGuard(ContextGuard.SkipContext()) as ctx_guard:
    if RUN_MEASUREMENT != 4:
        raise ctx_guard.Skip()
    ips8200hq.ips8200hq_out16a1_uvlo_concave_ramp(5, 10)

with ContextGuard(ContextGuard.SkipContext()) as ctx_guard:
    if RUN_MEASUREMENT != 3:
        raise ctx_guard.Skip()
    ips8200hq.ips8200hq_out16a1_input_convex_ramp(5, 10)

with ContextGuard(ContextGuard.SkipContext()) as ctx_guard:
    if RUN_MEASUREMENT != 4:
        raise ctx_guard.Skip()
    ips8200hq.ips8200hq_out16a1_input_concave_ramp(5, 10)
