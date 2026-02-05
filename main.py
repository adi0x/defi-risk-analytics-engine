import requests
import pandas as pd
import json
from datetime import datetime

# ============================================================
# DEFI RISK ANALYTICS ENGINE
# ============================================================

AAVE_API = "https://api.v3.aave.com/graphql"
ETHERSCAN_API_KEY = "4PY6DH8Y2PHGQDANXQINDZ9WN32A6I2KP4" 

# ============================================================
# 1. GET AAVE MARKET DATA
# ============================================================
def get_aave_markets():
    """Fetch all Aave V3 lending markets on Ethereum"""
    
    query = """
    query {
      markets(request: { chainIds: [1] }) {
        reserves {
          underlyingToken {
            symbol
            name
          }
          size {
            usd
          }
          supplyInfo {
            apy {
              value
            }
            supplyCap {
              usd
            }
          }
          borrowInfo {
            apy {
              value
            }
            borrowCap {
              usd
            }
          }
        }
      }
    }
    """
    
    response = requests.post(AAVE_API, json={"query": query})
    data = response.json()
    
    reserves = data["data"]["markets"][0]["reserves"]
    
    parsed = []
    for r in reserves:
        borrow_info = r.get("borrowInfo")
        record = {
            "token": r["underlyingToken"]["symbol"],
            "name": r["underlyingToken"]["name"],
            "market_size_usd": round(float(r["size"]["usd"]), 2),
            "supply_apy_pct": round(float(r["supplyInfo"]["apy"]["value"]) * 100, 2),
            "borrow_apy_pct": round(float(borrow_info["apy"]["value"]) * 100, 2) if borrow_info else 0,
        }
        parsed.append(record)
    
    return pd.DataFrame(parsed)


# ============================================================
# 2. GET WALLET TRANSACTION HISTORY (from Task 2)
# ============================================================
def get_wallet_transactions(wallet_address, limit=50):
    """Fetch transaction history for a wallet"""
    
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=desc&apikey={ETHERSCAN_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if data["status"] != "1":
        return None
    
    parsed = []
    for tx in data["result"][:limit]:
        record = {
            "date": datetime.fromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d %H:%M"),
            "from": tx["from"][:10] + "...",
            "to": tx["to"][:10] + "..." if tx["to"] else "Contract",
            "value_eth": round(int(tx["value"]) / 10**18, 4),
            "gas_used": int(tx["gasUsed"]),
            "gas_price_gwei": round(int(tx["gasPrice"]) / 10**9, 2),
            "gas_fee_eth": round(int(tx["gasUsed"]) * int(tx["gasPrice"]) / 10**18, 6),
            "status": "Success" if tx["txreceipt_status"] == "1" else "Failed"
        }
        parsed.append(record)
    
    return pd.DataFrame(parsed)


# ============================================================
# 3. CALCULATE WALLET HEALTH SCORE
# ============================================================
def calculate_wallet_health_score(tx_df):
    """Calculate a health score based on wallet activity"""
    
    if tx_df is None or len(tx_df) == 0:
        return None
    
    score = 100  # Start with perfect score
    
    # Factor 1: Transaction success rate (max -20 points)
    success_rate = (tx_df["status"] == "Success").sum() / len(tx_df)
    if success_rate < 0.95:
        score -= (0.95 - success_rate) * 100
    
    # Factor 2: Gas efficiency (max -20 points)
    avg_gas_price = tx_df["gas_price_gwei"].mean()
    if avg_gas_price > 50:  # High gas price = inefficient
        score -= min(20, (avg_gas_price - 50) / 5)
    
    # Factor 3: Activity level (max -20 points)
    if len(tx_df) < 10:
        score -= 20  # Low activity = less data to assess
    
    # Factor 4: Total gas spent (informational)
    total_gas_eth = tx_df["gas_fee_eth"].sum()
    
    return {
        "score": round(max(0, score), 1),
        "success_rate": round(success_rate * 100, 1),
        "avg_gas_price_gwei": round(avg_gas_price, 2),
        "total_gas_spent_eth": round(total_gas_eth, 4),
        "transaction_count": len(tx_df)
    }


# ============================================================
# 4. ANALYZE LIQUIDATION RISK (simulated)
# ============================================================
def simulate_liquidation_risk(collateral_usd, debt_usd, liquidation_threshold=0.825):
    """
    Calculate health factor and liquidation risk
    Health Factor = (Collateral * Liquidation Threshold) / Debt
    Below 1.0 = liquidatable
    """
    
    if debt_usd == 0:
        return {
            "health_factor": float('inf'),
            "risk_level": "No Debt",
            "liquidation_price_drop": 100
        }
    
    health_factor = (collateral_usd * liquidation_threshold) / debt_usd
    
    # How much can price drop before liquidation?
    price_drop_tolerance = ((health_factor - 1) / health_factor) * 100 if health_factor > 1 else 0
    
    if health_factor >= 2:
        risk_level = "LOW"
    elif health_factor >= 1.5:
        risk_level = "MEDIUM"
    elif health_factor >= 1.1:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    return {
        "health_factor": round(health_factor, 2),
        "risk_level": risk_level,
        "liquidation_price_drop": round(price_drop_tolerance, 1)
    }


# ============================================================
# 5. GENERATE RISK REPORT
# ============================================================
def generate_risk_report(wallet_address):
    """Generate a complete risk report for a wallet"""
    
    print("=" * 60)
    print("DEFI RISK ANALYTICS ENGINE")
    print("=" * 60)
    print(f"\nAnalyzing wallet: {wallet_address[:20]}...")
    
    # Get market data
    print("\n[1/4] Fetching Aave market data...")
    markets_df = get_aave_markets()
    print(f"     Found {len(markets_df)} lending markets")
    
    # Get wallet transactions
    print("\n[2/4] Fetching wallet transactions...")
    tx_df = get_wallet_transactions(wallet_address)
    if tx_df is not None:
        print(f"     Found {len(tx_df)} transactions")
    else:
        print("     No transactions found or error")
    
    # Calculate health score
    print("\n[3/4] Calculating wallet health score...")
    health = calculate_wallet_health_score(tx_df)
    
    # Simulate liquidation risk (example position)
    print("\n[4/4] Analyzing liquidation risk...")
    # Example: $10,000 collateral, $5,000 debt
    risk = simulate_liquidation_risk(10000, 5000)
    
    # Print report
    print("\n" + "=" * 60)
    print("RISK REPORT")
    print("=" * 60)
    
    if health:
        print(f"\n📊 WALLET HEALTH SCORE: {health['score']}/100")
        print(f"   - Success Rate: {health['success_rate']}%")
        print(f"   - Avg Gas Price: {health['avg_gas_price_gwei']} Gwei")
        print(f"   - Total Gas Spent: {health['total_gas_spent_eth']} ETH")
        print(f"   - Transactions Analyzed: {health['transaction_count']}")
    
    print(f"\n⚠️  LIQUIDATION RISK: {risk['risk_level']}")
    print(f"   - Health Factor: {risk['health_factor']}")
    print(f"   - Price can drop {risk['liquidation_price_drop']}% before liquidation")
    
    print("\n📈 TOP AAVE MARKETS BY SIZE:")
    print(markets_df.sort_values("market_size_usd", ascending=False).head(10).to_string(index=False))
    
    # Export
    markets_df.to_csv("aave_markets.csv", index=False)
    if tx_df is not None:
        tx_df.to_csv("wallet_transactions.csv", index=False)
    
    print("\n✅ Exported: aave_markets.csv, wallet_transactions.csv")
    print("=" * 60)
    
    return {
        "markets": markets_df,
        "transactions": tx_df,
        "health_score": health,
        "liquidation_risk": risk
    }


# ============================================================
# RUN THE ENGINE
# ============================================================
if __name__ == "__main__":
    # Use Vitalik's wallet as example (or any wallet you want to analyze)
    test_wallet = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    report = generate_risk_report(test_wallet)