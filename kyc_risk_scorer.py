"""
kyc_risk_scorer.py
------------------
A KYC (Know Your Customer) risk scoring tool that evaluates customers
based on AML (Anti-Money Laundering) risk factors and generates a report.

Risk factors assessed:
- Country risk (sanctions, high-risk jurisdictions)
- Business type risk
- Transaction volume & size
- PEP (Politically Exposed Person) status
- Cash-intensive business
- Length of relationship
"""

import pandas as pd
from datetime import datetime

# ── Risk Configuration ────────────────────────────────────────────────────────

# Country risk tiers based on FATF and common AML frameworks
COUNTRY_RISK = {
    # High risk / sanctioned
    "Iran": 100, "North Korea": 100, "Myanmar": 90,
    "Russia": 80, "Belarus": 75, "Afghanistan": 85,
    # Medium-high risk
    "Venezuela": 70, "Panama": 60, "China": 50,
    # Medium risk
    "Latvia": 20, "Poland": 15, "Lithuania": 15,
    # Low risk
    "Germany": 5, "Sweden": 5, "Norway": 5,
    "France": 5, "United Kingdom": 5, "United States": 10,
}

# Business type risk scores
BUSINESS_RISK = {
    "Shell Company": 90,
    "Cryptocurrency": 80,
    "Money Services": 75,
    "Real Estate": 60,
    "Import/Export": 50,
    "Construction": 45,
    "Consulting": 35,
    "Finance": 30,
    "Retail": 20,
    "Technology": 15,
    "Healthcare": 10,
}

# Risk thresholds for final classification
RISK_LEVELS = {
    (0, 30):   "🟢 LOW",
    (30, 60):  "🟡 MEDIUM",
    (60, 80):  "🟠 HIGH",
    (80, 101): "🔴 CRITICAL",
}


# ── Scoring Functions ─────────────────────────────────────────────────────────

def score_country(country: str) -> int:
    """Returns country risk score (0-100). Unknown countries get medium-high score."""
    return COUNTRY_RISK.get(country, 55)


def score_business(business_type: str) -> int:
    """Returns business type risk score (0-100)."""
    return BUSINESS_RISK.get(business_type, 40)


def score_transactions(annual_tx: int, avg_eur: float) -> int:
    """
    Scores transaction behavior.
    High volume + high average = higher risk (potential layering/structuring).
    """
    score = 0

    # Annual transaction volume
    if annual_tx > 700:
        score += 40
    elif annual_tx > 400:
        score += 25
    elif annual_tx > 200:
        score += 10

    # Average transaction size
    if avg_eur > 20000:
        score += 40
    elif avg_eur > 10000:
        score += 30
    elif avg_eur > 5000:
        score += 15
    elif avg_eur > 2000:
        score += 5

    return min(score, 100)


def score_pep(is_pep: bool) -> int:
    """PEP status adds significant risk — politically exposed persons require enhanced due diligence."""
    return 70 if is_pep else 0


def score_relationship(years: int) -> int:
    """New clients are higher risk — less history to verify behavior patterns."""
    if years == 0:
        return 40
    elif years <= 1:
        return 25
    elif years <= 3:
        return 10
    return 0


def score_cash(cash_intensive: bool) -> int:
    """Cash-intensive businesses are harder to verify and prone to smurfing."""
    return 35 if cash_intensive else 0


def get_risk_level(score: float) -> str:
    for (low, high), label in RISK_LEVELS.items():
        if low <= score < high:
            return label
    return "🔴 CRITICAL"


def calculate_risk(row: pd.Series) -> dict:
    """
    Calculates weighted composite risk score for a single customer.
    Weights reflect typical AML framework priorities.
    """
    weights = {
        "country":       0.25,
        "business":      0.20,
        "transactions":  0.20,
        "pep":           0.20,
        "relationship":  0.10,
        "cash":          0.05,
    }

    scores = {
        "country":      score_country(row["country"]),
        "business":     score_business(row["business_type"]),
        "transactions": score_transactions(row["annual_transactions"], row["transaction_avg_eur"]),
        "pep":          score_pep(row["is_pep"]),
        "relationship": score_relationship(row["years_as_client"]),
        "cash":         score_cash(row["cash_intensive"]),
    }

    composite = sum(scores[k] * weights[k] for k in scores)

    return {
        "composite_score": round(composite, 1),
        "risk_level": get_risk_level(composite),
        **{f"score_{k}": v for k, v in scores.items()},
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  KYC RISK SCORING ENGINE")
    print(f"  Run date: {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Load customer data
    df = pd.read_csv("customers.csv")

    # Convert boolean columns (CSV stores as strings)
    df["is_pep"] = df["is_pep"].astype(str).str.lower() == "true"
    df["cash_intensive"] = df["cash_intensive"].astype(str).str.lower() == "true"

    # Apply risk scoring
    risk_results = df.apply(calculate_risk, axis=1, result_type="expand")
    df = pd.concat([df, risk_results], axis=1)

    # Sort by risk score descending
    df = df.sort_values("composite_score", ascending=False).reset_index(drop=True)

    # ── Print Results ──────────────────────────────────────────────────────────
    print(f"\n{'RANK':<5} {'NAME':<20} {'COUNTRY':<15} {'BUSINESS TYPE':<20} {'SCORE':<8} {'RISK LEVEL'}")
    print("-" * 85)

    for _, row in df.iterrows():
        pep_flag = " ⚠️ PEP" if row["is_pep"] else ""
        print(f"{_+1:<5} {row['name']:<20} {row['country']:<15} {row['business_type']:<20} "
              f"{row['composite_score']:<8} {row['risk_level']}{pep_flag}")

    # ── Summary Statistics ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RISK DISTRIBUTION SUMMARY")
    print("=" * 60)

    total = len(df)
    critical = len(df[df["composite_score"] >= 80])
    high     = len(df[(df["composite_score"] >= 60) & (df["composite_score"] < 80)])
    medium   = len(df[(df["composite_score"] >= 30) & (df["composite_score"] < 60)])
    low      = len(df[df["composite_score"] < 30])

    print(f"  Total customers analysed : {total}")
    print(f"  🔴 Critical risk          : {critical} ({critical/total*100:.0f}%)")
    print(f"  🟠 High risk              : {high} ({high/total*100:.0f}%)")
    print(f"  🟡 Medium risk            : {medium} ({medium/total*100:.0f}%)")
    print(f"  🟢 Low risk               : {low} ({low/total*100:.0f}%)")
    print(f"\n  Average risk score       : {df['composite_score'].mean():.1f}")
    print(f"  Customers requiring EDD  : {critical + high} (High + Critical)")

    # ── Export ─────────────────────────────────────────────────────────────────
    output_file = "kyc_risk_report.csv"
    export_cols = ["customer_id", "name", "country", "business_type",
                   "is_pep", "composite_score", "risk_level",
                   "score_country", "score_business", "score_transactions",
                   "score_pep", "score_relationship", "score_cash"]
    df[export_cols].to_csv(output_file, index=False)

    print(f"\n  ✅ Full report saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
