"""
Screening Agent State Definition
=================================

State structure for the stock screening workflow.
"""

import operator
from typing import Annotated, List, TypedDict, Optional, Dict, Any

class ScreeningState(TypedDict):
    """
    State for stock screening workflow.

    Attributes:
    -----------
    criteria : str
        Investment criteria/strategy (e.g., "Warren Buffett value investing")

    max_stocks : int
        Maximum number of stocks to return in final recommendations

    sectors : Optional[List[str]]
        Filter by specific sectors if provided

    universe : List[str]
        Initial list of stock tickers to screen

    universe_size : int
        Count of stocks in initial universe

    candidates : List[Dict[str, Any]]
        Stocks that passed initial filters with their metrics

    filter_count : int
        Number of candidates after quick filter

    final_candidates : List[Dict[str, Any]]
        Top-ranked stocks after all scoring

    screening_complete : bool
        Flag indicating screening pipeline is complete

    portfolio_report : Optional[str]
        Final markdown report with recommendations
    """

    criteria: str
    max_stocks: int
    sectors: Optional[List[str]]
    universe: List[str]
    universe_size: int
    candidates: List[Dict[str, Any]]
    filter_count: int
    final_candidates: List[Dict[str, Any]]
    screening_complete: bool
    portfolio_report: Optional[str]
