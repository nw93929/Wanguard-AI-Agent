from evaluation.scorer import grade_report

def test_scorer_quality():
    bad_report = "The company is fine. Everything is okay."
    result = grade_report(bad_report)
    
    # We expect a low score for such a lazy report
    assert result.score < 50
    assert "depth" in result.critique.lower()