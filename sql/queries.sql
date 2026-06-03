-- Day 2: 10 Analytical Queries and Results

-- Generated on: 2026-06-03 22:17:29


-- Query 1: Top 5 funds by AUM
SELECT amfi_code, scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;;

/* RESULTS:
 amfi_code                                           scheme_name        fund_house  aum_crore
    148568 Mirae Asset Emerging Bluechip Fund - Regular - Growth    Mirae Asset MF    49046.0
    120842         Kotak Emerging Equity Fund - Regular - Growth Kotak Mahindra MF    47469.0
    118634        Nippon India Small Cap Fund - Regular - Growth   Nippon India MF    43630.0
    149322            DSP Top 100 Equity Fund - Regular - Growth   DSP Mutual Fund    41828.0
    102886                   UTI Mid Cap Fund - Regular - Growth   UTI Mutual Fund    41728.0
*/

--------------------------------------------------------------------------------

-- Query 2: Average NAV per month per scheme (Top 10 rows shown for brevity)
SELECT amfi_code, strftime('%Y-%m', nav_date) AS month, ROUND(AVG(nav), 4) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, month
ORDER BY amfi_code, month
LIMIT 10;;

/* RESULTS:
 amfi_code   month  avg_nav
    100016 2022-01 512.5353
    100016 2022-02 513.9306
    100016 2022-03 522.5782
    100016 2022-04 525.6312
    100016 2022-05 504.3125
    100016 2022-06 465.1370
    100016 2022-07 436.7460
    100016 2022-08 421.3311
    100016 2022-09 422.1759
    100016 2022-10 431.4175
*/

--------------------------------------------------------------------------------

-- Query 3: SIP Inflow and YoY Growth per month
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month;;

/* RESULTS:
  month  sip_inflow_crore  yoy_growth_pct
2022-01           11517.0             NaN
2022-02           11438.0             NaN
2022-03           12328.0             NaN
2022-04           11863.0             NaN
2022-05           12286.0             NaN
2022-06           12276.0             NaN
2022-07           12140.0             NaN
2022-08           12694.0             NaN
2022-09           12976.0             NaN
2022-10           13040.0             NaN
2022-11           13306.0             NaN
2022-12           13573.0             NaN
2023-01           13856.0           20.31
2023-02           13687.0           19.66
2023-03           14276.0           15.80
2023-04           14749.0           24.33
2023-05           14749.0           20.05
2023-06           14734.0           20.02
2023-07           15245.0           25.58
2023-08           15814.0           24.58
2023-09           16042.0           23.63
2023-10           16928.0           29.82
2023-11           17073.0           28.31
2023-12           17610.0           29.74
2024-01           18838.0           35.96
2024-02           19187.0           40.18
2024-03           20371.0           42.69
2024-04           20371.0           38.12
2024-05           21262.0           44.16
2024-06           21262.0           44.31
2024-07           23332.0           53.05
2024-08           23547.0           48.90
2024-09           24509.0           52.78
2024-10           25323.0           49.59
2024-11           25320.0           48.30
2024-12           26459.0           50.25
2025-01           26400.0           40.14
2025-02           25999.0           35.50
2025-03           25926.0           27.27
2025-04           26632.0           30.73
2025-05           26688.0           25.52
2025-06           27274.0           28.28
2025-07           28464.0           22.00
2025-08           28265.0           20.04
2025-09           29361.0           19.80
2025-10           29529.0           16.61
2025-11           30200.0           19.27
2025-12           31002.0           17.17
*/

--------------------------------------------------------------------------------

-- Query 4: Transactions and total amount by state
SELECT state, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;;

/* RESULTS:
         state  num_transactions  total_amount_inr
        Punjab              2965       315780459.0
    Tamil Nadu              2806       315177237.0
Madhya Pradesh              2931       308312493.0
     Rajasthan              2577       298645822.0
       Gujarat              2780       298358940.0
   West Bengal              2748       297182514.0
     Telangana              2718       290219284.0
         Delhi              2677       289633404.0
 Uttar Pradesh              2695       285368873.0
       Haryana              2736       279634354.0
     Karnataka              2621       273753570.0
   Maharashtra              2524       269513480.0
*/

--------------------------------------------------------------------------------

-- Query 5: Funds with expense ratio < 1%
SELECT amfi_code, scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;;

/* RESULTS:
 amfi_code                                          scheme_name               fund_house  expense_ratio_pct
    118636 Nippon India Gilt Securities Fund - Regular - Growth          Nippon India MF               0.55
    100025         HDFC Short Term Debt Fund - Regular - Growth         HDFC Mutual Fund               0.56
    120844                 Kotak Liquid Fund - Regular - Growth        Kotak Mahindra MF               0.60
    119552             SBI Bluechip Fund - Direct Plan - Growth          SBI Mutual Fund               0.66
    118633        Nippon India Large Cap Fund - Direct - Growth          Nippon India MF               0.72
    119599            SBI Small Cap Fund - Direct Plan - Growth          SBI Mutual Fund               0.72
    120507             ICICI Pru Liquid Fund - Regular - Growth      ICICI Prudential MF               0.74
    119093                 Axis Bluechip Fund - Direct - Growth         Axis Mutual Fund               0.75
    119120         SBI Magnum Gilt Fund - Regular Plan - Growth          SBI Mutual Fund               0.77
    125498    HDFC Mid-Cap Opportunities Fund - Direct - Growth         HDFC Mutual Fund               0.78
    101208                  ABSL Liquid Fund - Regular - Growth Aditya Birla Sun Life MF               0.79
    120504            ICICI Pru Bluechip Fund - Direct - Growth      ICICI Prudential MF               0.80
    118635                       Nippon India ETF Nifty 50 BeES          Nippon India MF               0.89
    125497             HDFC Top 100 Fund - Direct Plan - Growth         HDFC Mutual Fund               0.92
*/

--------------------------------------------------------------------------------

-- Query 6: Top 5 sectors by portfolio holding weight
SELECT sector, ROUND(SUM(weight_pct), 2) AS total_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC
LIMIT 5;;

/* RESULTS:
    sector  total_weight_pct
   Banking            652.26
        IT            455.47
    Pharma            407.45
Automobile            323.65
 Utilities            265.54
*/

--------------------------------------------------------------------------------

-- Query 7: Average transaction amount by age group and gender
SELECT age_group, gender, ROUND(AVG(amount_inr), 2) AS avg_transaction_amount_inr, COUNT(*) AS txn_count
FROM fact_transactions
GROUP BY age_group, gender
ORDER BY age_group, gender;;

/* RESULTS:
age_group gender  avg_transaction_amount_inr  txn_count
    18-25 Female                   108401.25       1722
    18-25   Male                   108006.40       3194
    26-35 Female                   106225.27       4379
    26-35   Male                   108590.90       9084
    36-45 Female                   108462.86       2705
    36-45   Male                   106277.43       5441
    46-55 Female                   110484.16       1270
    46-55   Male                   105656.27       2509
      56+ Female                   101693.58        893
      56+   Male                   107826.98       1581
*/

--------------------------------------------------------------------------------

-- Query 8: Top 3 performing funds based on 5-year returns
SELECT amfi_code, scheme_name, return_3yr_pct, return_5yr_pct
FROM fact_performance
ORDER BY return_5yr_pct DESC, return_3yr_pct DESC
LIMIT 3;;

/* RESULTS:
 amfi_code                                    scheme_name  return_3yr_pct  return_5yr_pct
    101207         ABSL Small Cap Fund - Regular - Growth           22.38           23.80
    119095         Axis Small Cap Fund - Regular - Growth           20.98           22.62
    118634 Nippon India Small Cap Fund - Regular - Growth           20.15           21.88
*/

--------------------------------------------------------------------------------

-- Query 9: High-risk schemes (High/Very High) with 1-year return < 12.0%
SELECT f.amfi_code, f.scheme_name, f.risk_category, p.return_1yr_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE f.risk_category IN ('Very High', 'High') AND p.return_1yr_pct < 12.0;;

/* RESULTS:
 amfi_code                                   scheme_name risk_category  return_1yr_pct
    148569 Mirae Asset Tax Saver Fund - Regular - Growth          High           11.16
*/

--------------------------------------------------------------------------------

-- Query 10: AUM growth by fund house between 2022-03-31 and 2025-12-31
SELECT fund_house, 
       ROUND(MAX(CASE WHEN date = '2022-03-31' THEN aum_crore END), 2) AS aum_2022_cr,
       ROUND(MAX(CASE WHEN date = '2025-12-31' THEN aum_crore END), 2) AS aum_2025_cr,
       ROUND(MAX(CASE WHEN date = '2025-12-31' THEN aum_crore END) - MAX(CASE WHEN date = '2022-03-31' THEN aum_crore END), 2) AS growth_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY growth_crore DESC;;

/* RESULTS:
              fund_house  aum_2022_cr  aum_2025_cr  growth_crore
         SBI Mutual Fund     605000.0    1250000.0      645000.0
     ICICI Prudential MF     465000.0    1074000.0      609000.0
        HDFC Mutual Fund     435000.0     930000.0      495000.0
         Nippon India MF     270000.0     700000.0      430000.0
       Kotak Mahindra MF     270000.0     580000.0      310000.0
          Mirae Asset MF     105000.0     290000.0      185000.0
Aditya Birla Sun Life MF     278000.0     460000.0      182000.0
         UTI Mutual Fund     230000.0     410000.0      180000.0
         DSP Mutual Fund     110000.0     230000.0      120000.0
        Axis Mutual Fund     250000.0     350000.0      100000.0
*/

--------------------------------------------------------------------------------
