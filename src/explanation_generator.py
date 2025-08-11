# src/explanation_generator.py
import sympy as sp

def _latex_block(obj) -> str:
    """Return a Markdown-ready LaTeX display block for a SymPy object or string."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return f"$$ {obj} $$"
    return f"$$ {sp.latex(obj)} $$"

def generate_explanation(problem: str) -> str:
    """
    Produce a friendly, human-style explanation.
    Returns Markdown text (contains LaTeX blocks like $$ ... $$).
    """
    try:
        x, y, z = sp.symbols("x y z")
        expr = sp.sympify(problem)

        # Start with a friendly line
        parts = []
        parts.append("**Here's what I found — short answer first, then a quick walkthrough:**")

        # Numeric expression
        if not expr.free_symbols and not isinstance(expr, (sp.Derivative, sp.Integral, sp.Equality)):
            val = sp.N(sp.simplify(expr))
            parts.append(f"**Short answer:** {val}")
            parts.append("")
            parts.append("**Walkthrough:**")
            parts.append(f"- I simplified the expression `{problem}` and evaluated it.")
            parts.append(_latex_block(val))
            return "\n\n".join(parts)

        # Derivative
        if isinstance(expr, sp.Derivative) or "diff(" in problem:
            deriv = expr.doit() if isinstance(expr, sp.Derivative) else sp.sympify(problem).doit()
            parts.append(f"**Short answer:** {sp.pretty(deriv)}")
            parts.append("")
            parts.append("**Walkthrough:**")
            parts.append(f"- You asked for the derivative of `{problem}`.")
            parts.append("- I applied the derivative rules and simplified the result:")
            parts.append(_latex_block(deriv))
            return "\n\n".join(parts)

        # Integral
        if isinstance(expr, sp.Integral) or "integrate(" in problem:
            integral = expr.doit() if isinstance(expr, sp.Integral) else sp.sympify(problem).doit()
            parts.append(f"**Short answer:** {sp.pretty(integral)} + C")
            parts.append("")
            parts.append("**Walkthrough:**")
            parts.append(f"- You requested an integral for `{problem}`.")
            parts.append("- I computed the antiderivative:")
            parts.append(_latex_block(integral))
            parts.append("- (Remember to add the constant of integration: `+ C`)")
            return "\n\n".join(parts)

        # Explicit equation Eq(...)
        if isinstance(expr, sp.Equality):
            parts.append("**Short answer:** I solved the equation and listed the solution(s) below.")
            parts.append("")
            parts.append("**Walkthrough:**")
            lhs, rhs = expr.lhs, expr.rhs
            canonical = sp.simplify(lhs - rhs)
            parts.append("- I rewrote the equation in canonical form (left - right = 0):")
            parts.append(_latex_block(sp.Eq(canonical, 0)))
            sol = sp.solve(expr, dict=True)
            if not sol:
                parts.append("- I couldn't find a solution.")
                return "\n\n".join(parts)
            for d in sol:
                for var, val in d.items():
                    parts.append(f"- Solution: {var} =")
                    parts.append(_latex_block(sp.Eq(var, val)))
            return "\n\n".join(parts)

        # General symbolic expression -> attempt to solve expr == 0
        parts.append("**Short answer:** I treated this as an equation `... = 0` and tried to solve for the main variable.")
        parts.append("")
        parts.append("**Walkthrough:**")
        vars_list = list(expr.free_symbols)
        primary_var = vars_list[0]
        parts.append(f"- Primary variable chosen: `{primary_var}`")
        # Factor if helpful
        try:
            fact = sp.factor(expr)
            if fact != expr:
                parts.append("- I checked for factorization and found:")
                parts.append(_latex_block(fact))
        except Exception:
            pass

        parts.append("- I solved the equation:")
        parts.append(_latex_block(sp.Eq(expr, 0)))
        sol_values = sp.solve(sp.Eq(expr, 0), primary_var)
        if not sol_values:
            simplified = sp.simplify(expr)
            parts.append("- I couldn't find algebraic roots; here is the simplified expression:")
            parts.append(_latex_block(simplified))
            return "\n\n".join(parts)

        # present solutions
        if isinstance(sol_values, list):
            for v in sol_values:
                parts.append(f"- Solution:")
                parts.append(_latex_block(sp.Eq(primary_var, v)))
        else:
            parts.append(f"- Solution:")
            parts.append(_latex_block(sp.Eq(primary_var, sol_values)))

        return "\n\n".join(parts)

    except Exception as e:
        return f"**Sorry — I couldn't generate a walkthrough.**\n\nError: {e}"
