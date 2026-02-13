
import asyncio
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from server.client import OfficeClient
from returns.result import Success, Failure

async def main():
    load_dotenv()
    
    base_url = os.getenv("UG_OFFICE_URL")
    username = os.getenv("UG_USERNAME")
    password = os.getenv("UG_PASSWORD")
    
    if not all([base_url, username, password]):
        print("Error: Missing credentials in .env")
        return

    client = OfficeClient(base_url, username, password)
    
    # Calculate yesterday's date
    yesterday_str = "2026-02-12"
    
    print(f"Checking Win/Loss for: {yesterday_str}")
    
    params = {
        "page": 1,
        "per_page": 30,
        "currency": "USD",
        "currency_mode": 1,
        "internal": 0,
        "from": yesterday_str,
        "to": yesterday_str,
        "group_by": "currency_id",
    }
    
    # Use the correct path based on src/server/tools/reports.py which uses PREFIX = "/1.0/reports"
    result = await client.request("GET", "/1.0/reports/winloss/all", params=params)
    
    match result:
        case Success(data):
            rows = data.get("data", []) if isinstance(data, dict) else data
            
            # Use the logic from reports.py to compute totals
            total = {
                "_summary": "USD TOTAL",
                "ticket": sum(r.get("ticket", 0) for r in rows),
                "net_turnover_usd": sum(r.get("to_usd_net_turnover", 0) for r in rows),
                "stake_usd": sum(r.get("to_usd_stake", 0) for r in rows),
                # "price_usd": sum(r.get("to_usd_price", 0) for r in rows), # Not in response sometimes?
                "payout_usd": sum(r.get("to_usd_payout", 0) for r in rows),
                "winloss_usd": sum(r.get("to_usd_winloss", 0) for r in rows),
                "net_winloss_usd": sum(r.get("to_usd_net_winloss", 0) for r in rows),
                "cashout_stake_usd": sum(r.get("to_usd_cashout_stake", 0) for r in rows),
                "cashout_usd": sum(r.get("to_usd_cashout", 0) for r in rows),
                "cashout_winloss_usd": sum(r.get("to_usd_cashout_winloss", 0) for r in rows),
            }
            net_to = total["net_turnover_usd"]
            if net_to:
                total["margin_pct"] = round((total["net_winloss_usd"] / net_to) * 100, 2)
            else:
                total["margin_pct"] = 0
            
            print("\n--- Win/Loss Report ---")
            print(f"Tickets: {total['ticket']}")
            print(f"Net Turnover (USD): {total['net_turnover_usd']:.2f}")
            print(f"Net Win/Loss (USD): {total['net_winloss_usd']:.2f}")
            print(f"Margin %: {total['margin_pct']}%")
            
        case Failure(err):
            print(f"Error fetching report: {err}")

if __name__ == "__main__":
    asyncio.run(main())
