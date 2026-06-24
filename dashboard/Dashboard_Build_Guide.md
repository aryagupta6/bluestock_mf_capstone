# Bluestock Mutual Fund Analytics: Dashboard Build Guide

This guide walks you through building the 4-page interactive dashboard in Power BI or Tableau. By using the pre-aggregated CSV datasets in `data/processed/`, you can construct this report without writing complex calculations inside the BI tool.

---

## Brand Theme & Styling

To ensure the dashboard matches the Bluestock brand identity, configure your custom report theme with these hex color codes:
- **Primary Color (Dark Navy):** `#0A2540` (Used for headers, KPI background cards, and primary chart elements)
- **Secondary Color (Steel Blue):** `#20639B` (Used for benchmark series and secondary chart series)
- **Accent Color (Gold/Amber):** `#F6D55C` (Used for milestones, highlights, and stars)
- **Neutral Dark (Text/Grid):** `#333333` (Used for axis labels and text body)
- **Neutral Light (Background):** `#F4F6F9` (Used for the workspace canvas background)
- **KPI Background Card:** `#FFFFFF` with a subtle grey border (`#E5E5E5`) and rounded corners (8px radius)

---

## Data Connections & Modeling

### 1. Import the Datasets
Open Power BI Desktop (or Tableau) and load the following files from your `data/processed/` folder using the **Text/CSV** connector:
1. `dashboard_page1_kpis.csv`
2. `dashboard_page1_aum_trend.csv`
3. `dashboard_page1_amc_aum.csv`
4. `dashboard_page2_performance.csv`
5. `dashboard_page2_nav.csv`
6. `dashboard_page3_transactions.csv`
7. `dashboard_page4_market_trends.csv`
8. `dashboard_page4_category_inflows.csv`

### 2. Set Up Relationships
Go to the **Model View** tab and configure these active relationships (ensure cross-filter direction is set to "Single" and cardinality is 1-to-many):
- `dashboard_page2_performance.amfi_code` (1) $\rightarrow$ `dashboard_page2_nav.amfi_code` (Many)
- `dashboard_page2_performance.amfi_code` (1) $\rightarrow$ `dashboard_page3_transactions.amfi_code` (Many)

---

## Page-by-Page Visual Layout

### Page 1: Industry Overview
*This page provides a high-level macroeconomic summary of the mutual fund industry.*

1. **Top Header Bar:** 
   - A dark navy bar (`#0A2540`) spanning the top. Place the Bluestock logo on the left and title *"Indian Mutual Fund Industry Overview"* on the right.
2. **KPI Cards (Top Row):** 
   - Create 4 separate card visuals using `dashboard_page1_kpis.csv`:
     - **Total AUM:** `total_aum_lakh_crore` $\rightarrow$ Format as `Rs. 81.0 Lakh Cr`
     - **Monthly SIP Inflow:** `monthly_sip_inflow_crore` $\rightarrow$ Format as `Rs. 31,002 Cr`
     - **Active Folios:** `total_folios_crore` $\rightarrow$ Format as `26.12 Cr`
     - **Active Schemes:** `total_schemes_count` $\rightarrow$ Format as `1,908`
3. **Line Chart (Left Panel):**
   - **Data source:** `dashboard_page1_aum_trend.csv`
   - **X-axis:** `date`, **Y-axis:** `total_aum_lakh_crore`
   - **Format:** Smooth line chart in Steel Blue (`#20639B`). Add data labels to show the progression from 2022 to late 2025.
4. **Horizontal Bar Chart (Right Panel):**
   - **Data source:** `dashboard_page1_amc_aum.csv`
   - **X-axis (Values):** `aum_lakh_crore`, **Y-axis (Categories):** `fund_house`
   - **Format:** Sort by AUM descending. Keep the top 10 AMC bars. Color SBI Mutual Fund's bar with `#0A2540` and others with `#20639B`.

---

### Page 2: Fund Performance Analytics
*This page allows users to screen and compare individual mutual fund schemes based on risk and return metrics.*

1. **Slicers (Top Panel):**
   - Place three interactive dropdown slicers at the top of the canvas:
     - **Fund House** (`dashboard_page2_performance.fund_house` or from master)
     - **Category** (`dashboard_page2_performance.category`)
     - **Plan** (Regular vs. Direct)
2. **Scatter Plot (Left Panel):**
   - **Data source:** `dashboard_page2_performance.csv`
   - **X-axis:** `cagr_3yr` (Return)
   - **Y-axis:** `sharpe_ratio` (or annualized std dev)
   - **Details/Legend:** `scheme_name`
   - **Bubble Size:** `overall_rank` (inverted, or map to total AUM so larger bubbles represent bigger funds)
3. **Scorecard Grid Table (Right Panel):**
   - **Data source:** `dashboard_page2_performance.csv`
   - **Columns:** `overall_rank`, `scheme_name`, `category`, `sub_category`, `cagr_3yr`, `sharpe_ratio`, `sortino_ratio`, `max_drawdown_pct`, `expense_ratio_pct`, `weighted_score`
   - **Formatting:** Turn on conditional formatting (data bars or soft background color scales) for `weighted_score` and `max_drawdown_pct`.
4. **Daily NAV Line Chart (Bottom Panel):**
   - **Data source:** `dashboard_page2_nav.csv`
   - **X-axis:** `nav_date`, **Y-axis:** `nav` and `benchmark_close` (dual axes or normalized)
   - **Formatting:** This chart updates automatically when you click a fund in the scorecard table above.

---

### Page 3: Investor Behaviour & Demographics
*This page analyzes investor transaction patterns across demographics and geographies.*

1. **State-wise Choropleth Map (Left Panel):**
   - **Data source:** `dashboard_page3_transactions.csv`
   - **Location:** `state`, **Color Saturation/Bubble Size:** `amount_inr` (Sum)
   - **Format:** Set map projection to India. Highlight major hubs (e.g., Maharashtra, Karnataka, Delhi) with darker shades of `#20639B`.
2. **Donut Chart (Right Top):**
   - **Data source:** `dashboard_page3_transactions.csv`
   - **Legend:** `transaction_type` (SIP vs. Lumpsum vs. Redemption)
   - **Values:** `amount_inr` (Sum)
3. **Clustered Column Chart (Right Bottom):**
   - **Data source:** `dashboard_page3_transactions.csv`
   - **X-axis:** `age_group` (18-25, 26-35, 36-45, 46-55, 56+), **Y-axis:** `amount_inr` (Average)
   - **Formatting:** Color columns with `#20639B`. Add a reference line indicating the average SIP ticket size across the entire database.
4. **Demographics Slicers:**
   - Add two vertical slicers on the side: **Gender** and **City Tier (T30 vs. B30)**.

---

### Page 4: SIP & Market Trends
*This page benchmarks systematic investment inflows against stock market indices.*

1. **Dual-Axis Chart (Top Panel):**
   - **Data source:** `dashboard_page4_market_trends.csv`
   - **X-axis:** `month`
   - **Column Y-axis:** `sip_inflow_crore` (Represented as clustered columns in `#20639B`)
   - **Line Y-axis:** `avg_nifty50_close` (Represented as a smooth line in `#0A2540` or `#F6D55C`)
   - **Insight:** Demonstrates how retail SIP inflows continued to climb even during market consolidation phases.
2. **Inflow Heatmap Grid (Bottom Left):**
   - **Data source:** `dashboard_page4_category_inflows.csv`
   - **Rows:** `category`, **Columns:** `month`, **Values:** `net_inflow_crore`
   - **Format:** Use a matrix visual. Apply conditional formatting (diverging color scale: light red for negative net inflows/redemptions, light green for positive inflows).
3. **Clustered Bar Chart (Bottom Right):**
   - **Data source:** `dashboard_page4_category_inflows.csv`
   - **Y-axis:** `category`, **X-axis:** `net_inflow_crore` (Sum)
   - **Sorting:** Sort descending to display the top categories bringing in the most net capital.

---

## Interactive Configurations & Tooltips

1. **Drill-Through (Fund details):**
   - Configure a drill-through filter on a separate detail page. Right-clicking a fund name in the scorecard on Page 2 should let you click "Drill-Through" to open a focused sheet displaying its full transaction log, portfolio holdings, and manager details.
2. **Hover Tooltip Cards:**
   - Create a hidden tooltip page. Format it as a small tooltip size (320px x 240px). 
   - Add a small card with the fund manager's name, exit load details, and the launch date.
   - Link this tooltip page to the scorecard table on Page 2 so hover events display these details instantly.
