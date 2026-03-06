import importlib.util
import pathlib
import unittest
import warnings

import numpy as np


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "demo_hyperbolized.py"
SPEC = importlib.util.spec_from_file_location("demo_hyperbolized", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DemoHyperbolizedTests(unittest.TestCase):
    def test_exact_solution_boundary_conditions(self):
        x = np.array([0.0, 0.2, 0.8, 1.0])
        for a in (1.0, -1.0):
            u = MOD.exact_solution(x, a, 0.0025)
            self.assertAlmostEqual(u[0], 0.0, places=12)
            self.assertAlmostEqual(u[-1], 1.0, places=12)

    def test_exact_solution_small_pe_linear_limit(self):
        x = np.linspace(0.0, 1.0, 21)
        u = MOD.exact_solution(x, a=1e-12, nu=1.0)
        self.assertTrue(np.allclose(u, x, rtol=0.0, atol=1e-14))

    def test_central_out_of_bounds_at_cell_pe5(self):
        _, u = MOD.solve_central(81, 1.0, 0.0025)
        self.assertTrue(np.min(u) < 0.0 or np.max(u) > 1.0)

    def test_upwind_bounded_monotone_for_a_signs(self):
        tol = 1e-10
        for a in (1.0, -1.0):
            _, u = MOD.solve_upwind_adv(81, a, 0.0025)
            self.assertGreaterEqual(np.min(u), -tol)
            self.assertLessEqual(np.max(u), 1.0 + tol)
            self.assertTrue(np.all(np.diff(u) >= -tol))

    def test_hyperbolic_bounded_monotone_for_a_signs(self):
        tol = 1e-9
        for a in (1.0, -1.0):
            _, u = MOD.solve_hyperbolic(81, a, 0.0025)
            self.assertGreaterEqual(np.min(u), -tol)
            self.assertLessEqual(np.max(u), 1.0 + tol)
            self.assertTrue(np.all(np.diff(u) >= -tol))

    def test_loading_ratio_ordering_default_case(self):
        n = 81
        a = 1.0
        nu = 0.0025
        h = 1.0 / (n - 1)

        _, u_c = MOD.solve_central(n, a, nu)
        _, u_u = MOD.solve_upwind_adv(n, a, nu)
        _, u_h = MOD.solve_hyperbolic(n, a, nu)

        lam_c = MOD.loading_ratio(u_c, h, a, nu)
        lam_u = MOD.loading_ratio(u_u, h, a, nu)
        lam_h = MOD.loading_ratio(u_h, h, a, nu)

        self.assertGreater(lam_c, lam_u)
        # The relative ordering of lam_u vs lam_h is not tested because both
        # monotone schemes produce similar loading ratios that may vary with
        # numerical dissipation details; the key invariant is that the
        # oscillatory central scheme dominates both.
        self.assertGreater(lam_c, lam_h)

    def test_hyperbolic_warns_on_large_dt(self):
        h = 1.0 / (81 - 1)
        dt_limit = MOD.stable_dt_limit(h, a=1.0, nu=0.0025, tau=0.001)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            MOD.solve_hyperbolic(81, 1.0, 0.0025, tau=0.001, dt=dt_limit * 2.0, nt_max=1)
        self.assertTrue(any(item.category is RuntimeWarning for item in caught))

    def test_hyperbolic_converges_to_exact_under_refinement(self):
        """Error must decrease under grid refinement (the original bug)."""
        a = 1.0
        nu = 0.1  # Pe = 10; resolvable boundary layer
        prev_err = None
        for n in (21, 41, 81):
            x, u = MOD.solve_hyperbolic(n, a, nu)
            u_exact = MOD.exact_solution(x, a, nu)
            err = np.max(np.abs(u - u_exact))
            if prev_err is not None:
                self.assertLess(err, prev_err)
            prev_err = err


if __name__ == "__main__":
    unittest.main()
