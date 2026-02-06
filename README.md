# DeFi Risk Analytics Engine
## Live Dashboard

🔗 [View Aave V3 Liquidation Monitor on Dune](https://dune.com/adu0x/aave-v3-liquidation-monitor)

A Python-based tool that analyzes wallet health and liquidation risk for DeFi lending protocols.

## What it does

1. **Fetches Aave V3 market data** — all lending markets, APYs, market sizes ($37B+ TVL)
2. **Analyzes wallet transactions** — gas efficiency, success rate, activity patterns
3. **Calculates wallet health score** — 0-100 score based on on-chain behavior
4. **Assesses liquidation risk** — health factor, risk level, price drop tolerance

## Sample Output
```
WALLET HEALTH SCORE: 100/100
- Success Rate: 96.0%
- Avg Gas Price: 0.88 Gwei
- Total Gas Spent: 0.0042 ETH

LIQUIDATION RISK: MEDIUM
- Health Factor: 1.65
- Price can drop 39.4% before liquidation

TOP AAVE MARKETS BY SIZE:
WETH    $6.5B   1.81% supply APY
USDT    $6.4B   2.23% supply APY
USDC    $4.3B   3.01% supply APY
```

## Tech Stack

- Python 3
- Aave V3 GraphQL API
- Etherscan API
- Pandas

## How to run

1. Clone this repo
2. Install dependencies: `pip install requests pandas`
3. Add your Etherscan API key in `main.py`
4. Run: `python main.py`

## Data Sources

| Source | Data |
|--------|------|
| Aave V3 GraphQL API | Lending markets, APYs, TVL |
| Etherscan API | Wallet transactions, gas data |

## Files

- `main.py` — Main analytics engine
- `aave_markets.csv` — Exported Aave market data
- `wallet_transactions.csv` — Exported wallet transaction history

## Future Improvements

- Real-time liquidation alerts
- Multi-chain support (Arbitrum, Polygon, Base)
- Dune Analytics dashboard integration
- Historical health factor tracking

## Author

Adithi Koppula
