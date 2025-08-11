from src.solver import solve_math_problem

def test_basic_equation():
    assert solve_math_problem("x - 2") == [2]
