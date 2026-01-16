# Stock Screening Mode Guide

## Overview

The AI Research Agent now supports **batch stock screening** to identify high-potential investments from thousands of stocks. Instead of analyzing one stock at a time, the screening mode:

1. Fetches a universe of stocks (S&P 500, Russell 2000, etc.)
2. Applies quantitative filters to narrow down candidates
3. Analyzes insider trading activity (SEC Form 4 filings)
4. Scores stocks against proven investment strategies
5. Returns a ranked portfolio of top 10-20 recommendations

## How It Works

### Architecture

```
┌──────────────┐    ┌─────────────┐     ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Universe   │───▶│ Quick Filter│───▶│   Insider  │───▶│  Strategy    │───▶│  Portfolio   │
│   Builder    │    │  (500→100)  │     │  Analysis   │    │  Scorer      │    │ Constructor  │
└──────────────┘    └─────────────┘     └─────────────┘    └──────────────┘    └──────────────┘
```

### Stage 1: Universe Building
- Fetches list of stocks to screen (default: S&P 500)
- Can filter by market cap, sector, or geographic region
- Typical size: 500-3000 stocks

### Stage 2: Quick Filter
Applies hard quantitative filters to eliminate unqualified stocks:
- Market cap > $1B (avoid micro-caps)
- Positive net income (profitable)
- Debt-to-Equity < 1.0 (manageable leverage)
- ROE > 15% (efficient capital use)
- Current Ratio > 1.5 (adequate liquidity)

**Result**: Narrows 500 stocks → ~50-100 candidates

### Stage 3: Insider Trading Analysis
Analyzes SEC Form 4 filings for bullish insider signals:
- **Strong signals**: CEO/CFO purchases, cluster buying, large amounts (> $1M)
- **Neutral**: Routine option exercises, single small purchases
- **Bearish**: Multiple executives selling, C-suite dumping shares

Each stock receives an insider score (0-100).

### Stage 4: Strategy Scoring
Scores remaining candidates against famous investor frameworks:

**Warren Buffett (Value + Moat)**
- Economic moat: Brand power, network effects, cost advantages
- Consistent 10-year earnings growth
- Low debt (D/E < 0.5)
- High ROE (> 15%)
- Shareholder-friendly management

**Peter Lynch (Growth at Reasonable Price)**
- PEG ratio < 1 (undervalued growth)
- 15-25% annual earnings growth
- P/E between 15-25
- Understandable business model
- Industry tailwinds

**Benjamin Graham (Deep Value)**
- P/E < 15, P/B < 1.5
- Dividend yield > 2%
- Strong balance sheet (Current Ratio > 2)
- Trading below intrinsic value

Each stock gets a strategy score (0-100). Final score = 50% insider + 50% strategy.

### Stage 5: Portfolio Construction
- Ranks top 10-20 stocks by combined score
- Ensures sector diversification (max 20% per sector)
- Suggests position sizing based on conviction
- Provides entry strategy (DCA vs lump sum)

## API Usage

### Single Stock Analysis (Existing)
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "instructions": "Analyze Q4 2024 financial performance"
  }'
```

### Stock Screening (New)
```bash
curl -X POST http://localhost:8000/research/screen \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "screening",
    "criteria": "Warren Buffett value investing",
    "max_stocks": 10,
    "sectors": ["Technology", "Healthcare"]
  }'
```

## n8n Integration

### Workflow Example
```
┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐
│ Schedule│───▶│  Webhook │───▶│ AI Research │───▶│  Notion  │
│ (Daily) │    │  (n8n)   │    │   Agent     │    │ Database │
└─────────┘    └──────────┘    └─────────────┘    └──────────┘
```

1. **Trigger**: Schedule node (run daily at 9 AM)
2. **HTTP Request**: POST to `/research/screen`
3. **Wait**: Poll for results (or use webhooks)
4. **Parse**: Extract top 10 stocks from response
5. **Store**: Save to Notion/Airtable/Google Sheets

## Data Sources

### Financial Modeling Prep (FMP)
- **Free tier**: 250 API calls/day
- **Data**: Fundamentals, insider trades, price history
- **Sign up**: https://financialmodelingprep.com/developer/docs/

### SEC EDGAR API
- **Free**: Unlimited (with rate limiting)
- **Data**: Form 4 insider trading filings, 10-K/10-Q reports
- **Docs**: https://www.sec.gov/edgar/sec-api-documentation

### Alpha Vantage (Backup)
- **Free tier**: 5 calls/minute, 500/day
- **Data**: Real-time quotes, technical indicators
- **Sign up**: https://www.alphavantage.co/

## Environment Setup

### Required API Keys
```bash
# .env file (DO NOT commit!)
OPENAI_API_KEY=sk-...
FMP_API_KEY=your-key-here
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=financial-docs
```

### Docker Compose
```bash
# Start all services
docker-compose up --build

# Start API only
docker-compose up agent_api

# View logs
docker-compose logs -f agent_api
```

## Performance

### Screening 500 Stocks
- **Stage 1 (Universe)**: 1 second
- **Stage 2 (Filter)**: 2-3 minutes (batch API calls)
- **Stage 3 (Insider)**: 3-5 minutes (1 call per stock)
- **Stage 4 (Scoring)**: 2-3 minutes (LLM analysis)
- **Stage 5 (Portfolio)**: 30 seconds

**Total**: 10-15 minutes for full screening

### Optimizations
- Parallel API calls (10 concurrent requests)
- Caching fundamentals data (refresh daily)
- LLM batching (score 5 stocks per prompt)

## Example Output

```markdown
# Recommended Stock Portfolio - Warren Buffett Strategy

## Executive Summary
- Total stocks: 10
- Expected risk profile: Low-Medium
- Diversification score: 8/10
- Recommended horizon: 5+ years

## Top 10 Holdings

| Rank | Ticker | Company            | Sector      | Score | Position | Rationale                          |
|------|--------|--------------------|-------------|-------|----------|------------------------------------|
| 1    | AAPL   | Apple Inc.         | Technology  | 94    | 12%      | Strong moat, 30% margins, cash    |
| 2    | BRK.B  | Berkshire Hathaway | Financials  | 91    | 12%      | Buffett's own company, diversified|
| 3    | JNJ    | Johnson & Johnson  | Healthcare  | 88    | 10%      | Dividend aristocrat, stable       |
...

## Sector Allocation
- Technology: 25%
- Healthcare: 20%
- Financials: 18%
- Consumer: 15%
- Industrials: 12%
- Energy: 10%

## Risk Analysis
- Portfolio Beta: 0.85 (less volatile than market)
- Expected annual volatility: 12%
- Max drawdown (2008 crisis): -32%

## Entry Strategy
- **Recommended**: Phased entry over 4 weeks (25% per week)
- **Rationale**: Reduce timing risk, smooth out volatility
- **Rebalance**: Quarterly, if position drifts +/- 20%

## Monitoring Plan
**Monthly tracking**:
- Quarterly earnings reports
- Insider trading activity
- Revenue/earnings growth trends

**Sell triggers**:
- Fundamental deterioration (3 consecutive quarters of declining margins)
- Strategy shift (company changes business model)
- Better opportunities emerge (rebalance into higher-scoring stocks)
```

## Customization

### Add Your Own Strategy
Edit `agents/prompts_screening.py`:
```python
MY_STRATEGY_SYSTEM = """
Score stocks based on:
1. High dividend yield (> 4%)
2. Low payout ratio (< 60%)
3. 10-year dividend growth
4. Stable cash flow
...
"""
```

### Change Universe
Edit `agents/screening_graph.py`:
```python
def universe_builder_node(state):
    # Use Russell 2000 instead of S&P 500
    tickers = fetch_russell2000_tickers()
    return {"universe": tickers}
```

### Adjust Filters
Edit `agents/screening_graph.py`:
```python
def quick_filter_node(state):
    # More aggressive filters
    if (market_cap > 5_000_000_000 and  # $5B+ only
        roe > 0.20 and                  # 20%+ ROE
        debt_to_equity < 0.3):          # Ultra-low debt
```

## Future Enhancements
- [ ] Real-time price alerts (when top picks hit buy price)
- [ ] Backtesting framework (test strategies on historical data)
- [ ] Portfolio tracker (monitor performance over time)
- [ ] Risk parity weighting (adjust for volatility)
- [ ] Short selling candidates (screen for overvalued stocks)

## Troubleshooting

**Error: "API rate limit exceeded"**
- Free tier FMP allows 250 calls/day
- Solution: Cache fundamentals data, reduce screening frequency

**Error: "No stocks passed filters"**
- Filters may be too strict
- Solution: Relax criteria (lower ROE threshold, higher D/E limit)

**Slow performance (> 30 min)**
- Batch API calls are sequential
- Solution: Implement async/parallel requests

## License
MIT - Use freely, attribution appreciated
