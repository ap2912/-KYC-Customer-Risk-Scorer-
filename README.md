# KYC Customer Risk Scorer

A Python-based KYC (Know Your Customer) risk scoring tool that evaluates customers against AML (Anti-Money Laundering) risk factors and generates a structured risk report.

Built as a practical project to demonstrate understanding of compliance frameworks used in banking and financial institutions.

# What it does

- Loads customer data from a CSV file
- Scores each customer across **6 weighted risk factors**
- Classifies customers as Low / Medium / High / Critical risk
- Flags customers requiring **Enhanced Due Diligence (EDD)**
- Exports a full risk report to CSV

## Risk Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Country Risk | 25% | Based on FATF ratings and sanctions lists |
| Business Type | 20% | Higher risk for shell companies, crypto, money services |
| Transaction Behavior | 20% | Volume and average transaction size |
| PEP Status | 20% | Politically Exposed Persons require stricter checks |
| Relationship Length | 10% | New clients carry higher uncertainty |
| Cash Intensity | 5% | Cash-heavy businesses are harder to verify |


# Risk Classification

| Score | Level |
|-------|-------|
| 0–30 | 🟢 Low |
| 30–60 | 🟡 Medium |
| 60–80 | 🟠 High |
| 80–100 | 🔴 Critical |

## Sample Output

```
RANK  NAME                 COUNTRY         BUSINESS TYPE        SCORE    RISK LEVEL
-------------------------------------------------------------------------------------
1     Hassan Khalid        Afghanistan     Money Services       70.0     🟠 HIGH ⚠️ PEP
2     Ivan Petrov          Russia          Cryptocurrency       63.5     🟠 HIGH ⚠️ PEP
3     Ahmed Al-Rashid      Iran            Money Services       56.8     🟡 MEDIUM
...
8     Maria Garcia         Germany         Import/Export        12.2     🟢 LOW

Total customers analysed : 15
Customers requiring EDD  : 2 (High + Critical)
```

---

## How to run

**Requirements:** Python 3.x, pandas

```bash
pip install pandas
python kyc_risk_scorer.py
```

Make sure `customers.csv` is in the same folder as the script. A `kyc_risk_report.csv` will be generated after each run.



## Files

| File | Description |
|------|-------------|
| `kyc_risk_scorer.py` | Main scoring engine |
| `customers.csv` | Sample customer input data |
| `kyc_risk_report.csv` | Generated risk report output |


## Key Concepts

- **KYC** — Know Your Customer: the process of verifying client identities and assessing their risk profile
- **AML** — Anti-Money Laundering: regulations to prevent financial crime
- **PEP** — Politically Exposed Person: individuals in prominent public roles who carry higher corruption risk
- **EDD** — Enhanced Due Diligence: deeper investigation required for high-risk customers
- **FATF** — Financial Action Task Force: global body that sets AML/KYC standards by country



## Author

Aditya Panwar — Computer Systems student at Riga Technical University
