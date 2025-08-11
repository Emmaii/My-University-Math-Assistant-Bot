# src/solver.py
import sympy as sp
from typing import Tuple

def _sympy_to_display(obj):
    """Return a simple human-readable string for a SymPy object."""
    try:
        # If it's a number, show as evaluated number
        if getattr(obj, "is_Number", False):
            return str(sp.N(obj))
        # For simpler readability, use pretty() but keep it one-line
        text = sp.pretty(obj)
        # collapse newlines to single space if any (so display stays compact)
        return " ".join(line.strip() for line in text.splitlines())
    except Exception:
        return str(obj)

def solve_math_problem(problem: str) -> Tuple[str, str]:
    """
    Parse input and return (display_text, latex_text).
    display_text: plain human-friendly string (always present)
    latex_text: LaTeX string for st.latex (may be empty if not useful)
    """
    try:
        x, y, z = sp.symbols("x y z")
        expr = sp.sympify(problem)

        # ---- Derivative ----
        if isinstance(expr, sp.Derivative) or "diff(" in problem:
            deriv = expr.doit() if isinstance(expr, sp.Derivative) else sp.sympify(problem).doit()
            display = _sympy_to_display(deriv)
            latex = sp.latex(deriv)
            return display, latex

        # ---- Integral ----
        if isinstance(expr, sp.Integral) or "integrate(" in problem:
            integral = expr.doit() if isinstance(expr, sp.Integral) else sp.sympify(problem).doit()
            display = _sympy_to_display(integral) + " + C"
            # add + C in LaTeX as well
            latex = sp.latex(integral) + r" + C"
            return display, latex

        # ---- Explicit equation Eq(...) ----
        if isinstance(expr, sp.Equality):
            sol = sp.solve(expr, dict=True)
            if not sol:
                return "No solution", r"\text{No solution}"

            display_parts = []
            latex_parts = []
            for sol_dict in sol:
                for var, val in sol_dict.items():
                    display_parts.append(f"{var} = {_sympy_to_display(val)}")
                    latex_parts.append(sp.latex(sp.Eq(var, val)))
            display = ", ".join(display_parts)
            # join latex pieces with small space
            latex = r"\; , \; ".join(latex_parts)
            return display, latex

        # ---- Numeric / constant expression ----
        if not expr.free_symbols:
            simplified = sp.simplify(expr)
            numeric = sp.N(simplified)
            display = _sympy_to_display(numeric)
            latex = sp.latex(numeric)
            return display, latex

        # ---- Expression with symbols: attempt to solve expr == 0 for first var ----
        vars_list = list(expr.free_symbols)
        primary_var = vars_list[0]

        sol_values = sp.solve(sp.Eq(expr, 0), primary_var)

        if sol_values:
            if isinstance(sol_values, list):
                display_parts = [f"{primary_var} = {_sympy_to_display(v)}" for v in sol_values]
                latex_parts = [sp.latex(sp.Eq(primary_var, v)) for v in sol_values]
                display = ", ".join(display_parts)
                latex = r"\; , \; ".join(latex_parts)
                return display, latex
            else:
                display = f"{primary_var} = {_sympy_to_display(sol_values)}"
                latex = sp.latex(sp.Eq(primary_var, sol_values))
                return display, latex

        # ---- Fallback: simplify and show expression (not a solved equation) ----
        simplified = sp.simplify(expr)
        display = _sympy_to_display(simplified)
        latex = sp.latex(simplified)
        return display, latex

    except Exception as e:
        # Friendly error fallback (always two strings)
        msg = f"Error: {str(e)}"
        latex_msg = r"\text{" + msg.replace("}", r"\}") + "}"
        return msg, latex_msg
