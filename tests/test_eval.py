from evaluation.scorer import score_report

def test_scorer_quality():
    bad_report = "The company is fine. Everything is okay."
    result = score_report(bad_report)
    
    # We expect a low score for such a lazy report
    assert result.score < 50
    assert "depth" in result.critique.lower()