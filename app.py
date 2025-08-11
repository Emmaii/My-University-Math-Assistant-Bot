from src.solver import solve_math_problem
from src.explanation_generator import generate_explanation

if __name__ == "__main__":
    problem = input("Enter your math problem: ")
    solution = solve_math_problem(problem)
    explanation = generate_explanation(problem)
    
    print("\nSolution:", solution)
    print("\nExplanation:", explanation)
