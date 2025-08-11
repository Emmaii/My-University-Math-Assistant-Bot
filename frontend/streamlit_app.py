# frontend/streamlit_app.py
import sys
import os

# Ensure project root is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import sympy as sp
from src.solver import solve_math_problem
from src.explanation_generator import generate_explanation

st.set_page_config(
    page_title="My University Math Assistant Bot",
    page_icon="📚",
    layout="centered",
)

st.title("📚 My University Math Assistant Bot")
st.write("Type a math expression or command. I'll give a short human answer and an optional formatted view.")
st.write("Examples: `2+2`, `x**2 - 4`, `diff(x**3, x)`, `integrate(x**2, x)`")

problem = st.text_area("Enter your problem:", placeholder="e.g. 2+2   |   x**2 - 4", height=140)

def _is_empty(s: str) -> bool:
    if s is None:
        return True
    s2 = str(s).strip()
    if not s2:
        return True
    empties = {"[]", "()", "Tuple()", "None", "NoneType"}
    return s2 in empties

def _sympy_fallback(problem_str: str):
    """Try to compute a readable (display, latex) fallback using sympy."""
    try:
        x, y, z = sp.symbols("x y z")
        expr = sp.sympify(problem_str)

        # derivative/integral quick handling
        if isinstance(expr, sp.Derivative) or "diff(" in problem_str:
            deriv = expr.doit() if isinstance(expr, sp.Derivative) else sp.sympify(problem_str).doit()
            return (str(sp.pretty(deriv)), str(sp.latex(deriv)))

        if isinstance(expr, sp.Integral) or "integrate(" in problem_str:
            integral = expr.doit() if isinstance(expr, sp.Integral) else sp.sympify(problem_str).doit()
            return (str(sp.pretty(integral)) + " + C", str(sp.latex(integral) + r" + C"))

        # numeric expression -> evaluate
        if not expr.free_symbols:
            val = sp.N(sp.simplify(expr))
            return (str(sp.pretty(val)), str(sp.latex(val)))

        # try to solve expr == 0 for first symbol
        vars_list = list(expr.free_symbols)
        if vars_list:
            primary = vars_list[0]
            sols = sp.solve(sp.Eq(expr, 0), primary)
            if sols:
                if isinstance(sols, list):
                    display = ", ".join([f"{primary} = {sp.pretty(s)}" for s in sols])
                    latex = r"\; , \; ".join([sp.latex(sp.Eq(primary, s)) for s in sols])
                    return (display, latex)
                else:
                    return (f"{primary} = {sp.pretty(sols)}", sp.latex(sp.Eq(primary, sols)))

        # fallback: simplify
        simplified = sp.simplify(expr)
        return (str(sp.pretty(simplified)), str(sp.latex(simplified)))
    except Exception as e:
        return (f"Error during fallback: {e}", r"\text{Error during fallback}")

if st.button("Solve"):
    if not problem or not problem.strip():
        st.warning("Please type a problem (e.g. `2+2`) then press Solve.")
    else:
        # Call solver - be defensive about what it returns
        try:
            raw = solve_math_problem(problem)
        except Exception as e:
            raw = f"Error: solver raised exception: {e}"

        # Normalize into display_text, latex_text
        display_text = ""
        latex_text = ""

        # If solver returned tuple/list with >=2 elements, use first two
        if isinstance(raw, (list, tuple)) and len(raw) >= 2:
            display_text, latex_text = str(raw[0]), str(raw[1])
        # If solver returned single string, use it as display_text
        elif isinstance(raw, str):
            display_text, latex_text = raw, ""
        # If solver returned None or empty, run fallback
        elif raw is None:
            display_text, latex_text = _sympy_fallback(problem)
        else:
            # Unknown type: try to coerce to str, then fallback if empty
            try:
                s = str(raw)
                if s and not _is_empty(s):
                    display_text, latex_text = s, ""
                else:
                    display_text, latex_text = _sympy_fallback(problem)
            except Exception:
                display_text, latex_text = _sympy_fallback(problem)

        # If both results look empty (or solver returned empties like "[]"), compute fallback
        if _is_empty(display_text) or _is_empty(latex_text):
            fb_display, fb_latex = _sympy_fallback(problem)
            if fb_display and not _is_empty(fb_display):
                display_text, latex_text = fb_display, fb_latex

        # ---- Render output: always show a human-friendly text answer first ----
        st.subheader("✅ Answer")
        if display_text and not display_text.lower().startswith("error"):
            st.markdown(f"**{display_text}**")
        else:
            st.markdown(f"**{display_text}**")  # show error plainly

        # Optionally show LaTeX formatted version if meaningful
        if latex_text and not _is_empty(latex_text) and not display_text.lower().startswith("error"):
            try:
                st.write("")  # spacing
                st.markdown("**Formatted:**")
                st.latex(latex_text)
            except Exception:
                pass

        # Quick note and walkthrough
        st.markdown("---")
        st.subheader("💬 Quick note")
        if display_text.lower().startswith("error"):
            st.write("I couldn't parse that input. Try a simpler form like `2+2` or `x**2 - 4`.")
        else:
            st.write("Above is the direct answer. Scroll down for a friendly walkthrough of steps.")

        st.markdown("---")
        st.subheader("📝 Walkthrough")
        try:
            explanation_md = generate_explanation(problem)
            if explanation_md and not _is_empty(explanation_md):
                st.markdown(explanation_md, unsafe_allow_html=True)
            else:
                st.write("No walkthrough available for this input.")
        except Exception:
            st.write("Couldn't produce a walkthrough for this input.")

        # Hidden debug info
        with st.expander("Show debug info"):
            st.write("Raw solver return:", repr(raw))
            st.write("display_text:", display_text)
            st.write("latex_text:", latex_text)
