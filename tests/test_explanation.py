from src.explanation_generator import generate_explanation

def test_explanation():
    result = generate_explanation("x - 2")
    assert "Solving equation gives" in result
