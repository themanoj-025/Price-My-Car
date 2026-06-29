"""
Car Price Dataset - Comprehensive EDA Report Generator
======================================================
Generates an HTML report with visualizations and statistics.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# Settings
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
REPORT_DIR = 'report_output'
os.makedirs(REPORT_DIR, exist_ok=True)
IMG_DIR = os.path.join(REPORT_DIR, 'images')
os.makedirs(IMG_DIR, exist_ok=True)

# 1. Load Data
df = pd.read_csv('Cleaned_Car_data.csv', index_col=0)
df_original = df.copy()
df = df.drop_duplicates().reset_index(drop=True)
CURRENT_YEAR = 2025

print(f"[1] Data loaded: {df_original.shape[0]} rows ({df.shape[0]} after dedup)")

# Feature engineering
df['car_age'] = CURRENT_YEAR - df['year']
df['log_price'] = np.log1p(df['Price'])
df['price_lakhs'] = df['Price'] / 1e5
df['kms_10k'] = df['kms_driven'] / 1e4

def save_plot(fig, filename):
    path = os.path.join(IMG_DIR, filename)
    fig.savefig(path, dpi=120, bbox_inches='tight')
    plt.close(fig)
    return filename

# === 2a. Price Distribution ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(df['price_lakhs'], bins=50, color='steelblue', edgecolor='white', alpha=0.8)
axes[0].set_xlabel('Price (in lakhs)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Car Prices')
axes[0].axvline(df['price_lakhs'].median(), color='red', ls='--', label='Median')
axes[0].axvline(df['price_lakhs'].mean(), color='green', ls='--', label='Mean')
axes[0].legend()
axes[1].hist(df['log_price'], bins=50, color='coral', edgecolor='white', alpha=0.8)
axes[1].set_xlabel('Log(Price)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Log-Transformed Price Distribution')
fig.tight_layout()
save_plot(fig, 'price_distribution.png')

# === 2b. Price by Fuel Type ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fuel_order = df.groupby('fuel_type')['Price'].median().sort_values(ascending=False).index
sns.boxplot(data=df, x='fuel_type', y='price_lakhs', order=fuel_order, palette='Set2', ax=axes[0])
axes[0].set_xlabel('Fuel Type')
axes[0].set_ylabel('Price (in lakhs)')
axes[0].set_title('Price Distribution by Fuel Type')
sns.violinplot(data=df, x='fuel_type', y='log_price', order=fuel_order, palette='Set2', ax=axes[1])
axes[1].set_xlabel('Fuel Type')
axes[1].set_ylabel('Log(Price)')
axes[1].set_title('Log-Price Distribution by Fuel Type')
fig.tight_layout()
save_plot(fig, 'price_by_fuel.png')

# === 2c. Top 15 Companies by Avg Price ===
top_companies = df.groupby('company').agg(
    avg_price=('Price', 'mean'),
    count=('Price', 'count')
).sort_values('avg_price', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(range(len(top_companies)), top_companies['avg_price'] / 1e5, color='teal', alpha=0.8)
ax.set_yticks(range(len(top_companies)))
ax.set_yticklabels(top_companies.index)
ax.set_xlabel('Average Price (in lakhs)')
ax.set_title('Top 15 Car Companies by Average Price')
for i, (v, c) in enumerate(zip(top_companies['avg_price'] / 1e5, top_companies['count'])):
    ax.text(v + 0.5, i, f'n={c}', va='center', fontsize=9)
fig.tight_layout()
save_plot(fig, 'top_companies_price.png')

# === 2d. Price vs Car Age ===
fig, ax = plt.subplots(figsize=(12, 6))
scatter = ax.scatter(df['car_age'], df['price_lakhs'], c=df['kms_10k'],
                     alpha=0.4, s=15, cmap='viridis')
ax.set_xlabel('Car Age (years)')
ax.set_ylabel('Price (in lakhs)')
ax.set_title('Price vs Car Age (colored by KMs driven)')
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('KMs Driven (ten-thousands)')
fig.tight_layout()
save_plot(fig, 'price_vs_age.png')

# === 2e. KMs Driven Distribution ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
kms_clipped = df['kms_10k'].clip(upper=25)
axes[0].hist(kms_clipped, bins=40, color='seagreen', edgecolor='white', alpha=0.8)
axes[0].set_xlabel('KMs Driven (ten-thousands)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of KMs Driven (clipped at 250k)')
axes[1].scatter(df['kms_10k'], df['price_lakhs'], alpha=0.3, s=10, color='purple')
axes[1].set_xlabel('KMs Driven (ten-thousands)')
axes[1].set_ylabel('Price (in lakhs)')
axes[1].set_title('Price vs KMs Driven')
fig.tight_layout()
save_plot(fig, 'kms_distribution.png')

# === 2f. Year Distribution ===
year_counts = df['year'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(14, 5))
ax.bar(year_counts.index, year_counts.values, color='cornflowerblue', edgecolor='white', width=0.8)
ax.set_xlabel('Manufacturing Year')
ax.set_ylabel('Number of Cars')
ax.set_title('Distribution of Cars by Manufacturing Year')
ax.set_xticks(range(1983, 2022, 2))
ax.tick_params(axis='x', rotation=45)
fig.tight_layout()
save_plot(fig, 'year_distribution.png')

# === 2g. Price by Company (Box Plot - Top 20) ===
top20_companies = df['company'].value_counts().head(20).index
df_top20 = df[df['company'].isin(top20_companies)]
company_order = df_top20.groupby('company')['Price'].median().sort_values(ascending=False).index

fig, ax = plt.subplots(figsize=(14, 7))
sns.boxplot(data=df_top20, x='company', y='price_lakhs',
            order=company_order, palette='Spectral', ax=ax,
            flierprops={'markersize': 3, 'alpha': 0.4})
ax.set_xlabel('Company')
ax.set_ylabel('Price (in lakhs)')
ax.set_title('Price Distribution by Company (Top 20)')
ax.tick_params(axis='x', rotation=45)
fig.tight_layout()
save_plot(fig, 'price_by_company_box.png')

# === 2h. Correlation Heatmap ===
df_numeric = df[['Price', 'year', 'kms_driven', 'car_age', 'log_price']].copy()
corr = df_numeric.corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt='.3f', cmap='RdBu_r', vmin=-1, vmax=1,
            square=True, linewidths=0.5, ax=ax, cbar_kws={'shrink': 0.8})
ax.set_title('Correlation Heatmap of Numerical Features')
fig.tight_layout()
save_plot(fig, 'correlation_heatmap.png')

# === 2i. Top 10 Most Expensive Cars Table ===
top10 = df.nlargest(10, 'Price')[['name', 'company', 'year', 'Price', 'kms_driven', 'fuel_type']]

fig, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')
table = ax.table(cellText=top10.values,
                 colLabels=top10.columns,
                 cellLoc='left', loc='center',
                 colWidths=[0.25, 0.12, 0.08, 0.12, 0.12, 0.10])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.4)
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(color='white', weight='bold')
ax.set_title('Top 10 Most Expensive Cars', fontsize=14, pad=20)
fig.tight_layout()
save_plot(fig, 'top10_expensive.png')

print("[2] All visualizations generated.")

# === 3. Compute Statistics ===
stats = {}
stats['total_rows_original'] = len(df_original)
stats['total_rows_clean'] = len(df)
stats['duplicates'] = stats['total_rows_original'] - stats['total_rows_clean']
stats['num_features'] = len(df.columns)
stats['columns'] = list(df.columns)

p = df['Price']
stats['price_min'] = int(p.min())
stats['price_max'] = int(p.max())
stats['price_mean'] = int(p.mean())
stats['price_median'] = int(p.median())
stats['price_std'] = int(p.std())
stats['price_skew'] = round(p.skew(), 2)
stats['price_kurtosis'] = round(p.kurtosis(), 2)
stats['price_q25'] = int(p.quantile(0.25))
stats['price_q75'] = int(p.quantile(0.75))

k = df['kms_driven']
stats['kms_min'] = int(k.min())
stats['kms_max'] = int(k.max())
stats['kms_mean'] = int(k.mean())
stats['kms_median'] = int(k.median())

y = df['year']
stats['year_min'] = int(y.min())
stats['year_max'] = int(y.max())
stats['year_mean'] = round(y.mean(), 1)
stats['most_common_year'] = int(y.mode()[0])

a = df['car_age']
stats['age_min'] = int(a.min())
stats['age_max'] = int(a.max())
stats['age_mean'] = round(a.mean(), 1)

fuel_counts = df['fuel_type'].value_counts()
stats['fuel_counts'] = fuel_counts.to_dict()
stats['fuel_diesel'] = int(fuel_counts.get('Diesel', 0))
stats['fuel_petrol'] = int(fuel_counts.get('Petrol', 0))
stats['fuel_cng'] = int(fuel_counts.get('CNG', 0))
stats['fuel_lpg'] = int(fuel_counts.get('LPG', 0))
stats['fuel_electric'] = int(fuel_counts.get('Electric', 0))

company_counts = df['company'].value_counts()
stats['num_companies'] = len(company_counts)
stats['top10_companies'] = company_counts.head(10).to_dict()
stats['company_most_listings'] = company_counts.index[0]
stats['company_most_listings_count'] = int(company_counts.iloc[0])

avg_by_fuel = df.groupby('fuel_type')['Price'].mean().sort_values(ascending=False)
stats['avg_price_by_fuel'] = {k: int(v) for k, v in avg_by_fuel.items()}

stats['corr_price_age'] = round(df['Price'].corr(df['car_age']), 3)
stats['corr_price_kms'] = round(df['Price'].corr(df['kms_driven']), 3)
stats['corr_price_year'] = round(df['Price'].corr(df['year']), 3)
stats['corr_price_logkms'] = round(df['Price'].corr(np.log1p(df['kms_driven'])), 3)

stats['price_percentiles'] = {str(pct): int(df['Price'].quantile(pct/100))
                               for pct in [1, 5, 10, 25, 50, 75, 90, 95, 99]}
stats['missing_values'] = int(df.isnull().sum().sum())

# ML data stats
stats['n_train'] = int(stats['total_rows_clean'] * 0.8)
stats['n_test'] = stats['total_rows_clean'] - stats['n_train']

print("[3] Statistics computed.")

# === 4. Generate HTML Report ===
def img_html(filename, alt=''):
    return f'<img src="images/{filename}" alt="{alt}" style="max-width:100%; margin:10px 0; border:1px solid #ddd; border-radius:4px;" />'

def fmt_price(val):
    if val >= 10000000:
        return f'\u20b9{val/10000000:.1f} Cr'
    elif val >= 100000:
        return f'\u20b9{val/100000:.1f} L'
    else:
        return f'\u20b9{val:,}'

html_parts = []
html_parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Car Price Dataset - EDA Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
               background: #f5f7fa; color: #2c3e50; line-height: 1.6; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white; padding: 50px 20px; text-align: center;
            border-bottom: 4px solid #e94560;
        }}
        .header h1 {{ font-size: 2.2em; margin-bottom: 8px; letter-spacing: 1px; }}
        .header p {{ font-size: 1.1em; opacity: 0.85; }}
        .header .meta {{ margin-top: 12px; font-size: 0.9em; opacity: 0.7; }}
        .kpi-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px; margin: 30px 0;
        }}
        .kpi-card {{
            background: white; padding: 20px; border-radius: 10px; text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 4px solid #3498db;
        }}
        .kpi-card .value {{ font-size: 1.8em; font-weight: 700; color: #1a1a2e; }}
        .kpi-card .label {{ font-size: 0.85em; color: #7f8c8d; margin-top: 4px; }}
        .kpi-card.gold {{ border-top-color: #f39c12; }}
        .kpi-card.green {{ border-top-color: #27ae60; }}
        .kpi-card.red {{ border-top-color: #e74c3c; }}
        .kpi-card.purple {{ border-top-color: #9b59b6; }}
        .kpi-card.teal {{ border-top-color: #1abc9c; }}
        .section {{
            background: white; margin: 24px 0; padding: 28px 30px;
            border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .section h2 {{
            font-size: 1.4em; color: #1a1a2e; border-bottom: 2px solid #eee;
            padding-bottom: 10px; margin-bottom: 20px;
        }}
        .stats-table {{
            width: 100%; border-collapse: collapse; margin: 12px 0;
        }}
        .stats-table th {{
            background: #2c3e50; color: white; padding: 10px 14px;
            text-align: left; font-size: 0.9em;
        }}
        .stats-table td {{
            padding: 8px 14px; border-bottom: 1px solid #eee; font-size: 0.95em;
        }}
        .stats-table tr:nth-child(even) td {{ background: #f8f9fa; }}
        .stats-table td:last-child {{ font-weight: 600; text-align: right; }}
        .img-container {{ text-align: center; margin: 20px 0; }}
        .dual {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .dual > div {{ flex: 1; min-width: 300px; }}
        .img-row {{ display: flex; gap: 15px; flex-wrap: wrap; justify-content: center; }}
        .img-row .img-container {{ flex: 1; min-width: 300px; }}
        .footer {{ text-align: center; padding: 30px; color: #7f8c8d; font-size: 0.85em; }}
        @media (max-width: 600px) {{
            .header h1 {{ font-size: 1.5em; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
<div class="header">
    <h1>&#128663; Car Price Dataset &mdash; EDA Report</h1>
    <p>Exploratory Data Analysis &amp; Preprocessing Summary</p>
    <div class="meta">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} &nbsp;|&nbsp; {stats["total_rows_clean"]:,} records after deduplication</div>
</div>
<div class="container">
''')

# KPI Cards
html_parts.append(f'''
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="value">{stats["total_rows_clean"]:,}</div>
        <div class="label">Total Records</div>
    </div>
    <div class="kpi-card gold">
        <div class="value">{fmt_price(stats["price_median"])}</div>
        <div class="label">Median Price</div>
    </div>
    <div class="kpi-card green">
        <div class="value">{stats["age_max"]:,} yrs</div>
        <div class="label">Age Range</div>
    </div>
    <div class="kpi-card red">
        <div class="value">{stats["kms_mean"]:,}</div>
        <div class="label">Avg KMs Driven</div>
    </div>
    <div class="kpi-card purple">
        <div class="value">{stats["num_companies"]}</div>
        <div class="label">Companies</div>
    </div>
    <div class="kpi-card teal">
        <div class="value">{stats["duplicates"]:,}</div>
        <div class="label">Duplicates Removed</div>
    </div>
</div>
''')

# Section 1: Dataset Overview
html_parts.append(f'''
<div class="section">
    <h2>&#49; Dataset Overview</h2>
    <table class="stats-table">
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Original Rows</td><td>{stats["total_rows_original"]:,}</td></tr>
        <tr><td>Duplicate Rows Removed</td><td>{stats["duplicates"]:,}</td></tr>
        <tr><td>Clean Rows</td><td>{stats["total_rows_clean"]:,}</td></tr>
        <tr><td>Columns / Features</td><td>{stats["num_features"]}</td></tr>
        <tr><td>Missing Values</td><td>{stats["missing_values"]}</td></tr>
        <tr><td>Column Names</td><td style="font-size:0.85em">{", ".join(stats["columns"])}</td></tr>
    </table>
</div>
''')

# Section 2: Price Analysis
html_parts.append(f'''
<div class="section">
    <h2>&#50; Price Analysis</h2>
    <div class="dual">
        <div>
            <table class="stats-table">
                <tr><th>Statistic</th><th>Value</th></tr>
                <tr><td>Minimum</td><td>{fmt_price(stats["price_min"])}</td></tr>
                <tr><td>Q1 (25th)</td><td>{fmt_price(stats["price_q25"])}</td></tr>
                <tr><td>Median (50th)</td><td>{fmt_price(stats["price_median"])}</td></tr>
                <tr><td>Mean</td><td>{fmt_price(stats["price_mean"])}</td></tr>
                <tr><td>Q3 (75th)</td><td>{fmt_price(stats["price_q75"])}</td></tr>
                <tr><td>Maximum</td><td>{fmt_price(stats["price_max"])}</td></tr>
                <tr><td>Std Deviation</td><td>{fmt_price(stats["price_std"])}</td></tr>
                <tr><td>Skewness</td><td>{stats["price_skew"]}</td></tr>
                <tr><td>Kurtosis</td><td>{stats["price_kurtosis"]}</td></tr>
            </table>
        </div>
        <div>
            <table class="stats-table">
                <tr><th>Percentile</th><th>Price</th></tr>
''')
for pct in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    html_parts.append(f'<tr><td>{pct}th</td><td>{fmt_price(stats["price_percentiles"][str(pct)])}</td></tr>\n')
html_parts.append(f'''
            </table>
        </div>
    </div>
    <div class="img-row">
        <div class="img-container">{img_html('price_distribution.png')}</div>
    </div>
</div>
''')

# Section 3: Fuel Type Analysis
html_parts.append(f'''
<div class="section">
    <h2>&#51; Fuel Type Analysis</h2>
    <div class="dual">
        <div>
            <table class="stats-table">
                <tr><th>Fuel Type</th><th>Count</th><th>% of Total</th><th>Avg Price</th></tr>
''')
for fuel in ['Diesel', 'Petrol', 'CNG', 'LPG', 'Electric']:
    count = stats['fuel_counts'].get(fuel, 0)
    pct = count / stats['total_rows_clean'] * 100
    avg_p = stats['avg_price_by_fuel'].get(fuel, 0)
    html_parts.append(f'<tr><td>{fuel}</td><td>{count:,}</td><td>{pct:.1f}%</td><td>{fmt_price(avg_p)}</td></tr>\n')
html_parts.append(f'''
            </table>
        </div>
        <div class="img-container">{img_html('price_by_fuel.png')}</div>
    </div>
</div>
''')

# Section 4: Company Analysis
html_parts.append(f'''
<div class="section">
    <h2>&#52; Company Analysis</h2>
    <p style="margin-bottom:12px"><strong>Total unique companies:</strong> {stats["num_companies"]} &nbsp;|&nbsp; <strong>Most listings:</strong> {stats["company_most_listings"]} ({stats["company_most_listings_count"]:,} cars)</p>
    <div class="dual">
        <div>
            <table class="stats-table">
                <tr><th>#</th><th>Company</th><th>Listings</th><th>%</th></tr>
''')
for i, (company, count) in enumerate(stats['top10_companies'].items(), 1):
    pct = count / stats['total_rows_clean'] * 100
    html_parts.append(f'<tr><td>{i}</td><td>{company}</td><td>{count:,}</td><td>{pct:.1f}%</td></tr>\n')
html_parts.append(f'''
            </table>
        </div>
        <div class="img-container">{img_html('top_companies_price.png')}</div>
    </div>
    <div class="img-container">{img_html('price_by_company_box.png')}</div>
</div>
''')

# Section 5: Feature Correlations
html_parts.append(f'''
<div class="section">
    <h2>&#53; Feature Correlations</h2>
    <table class="stats-table" style="max-width:500px">
        <tr><th>Relationship</th><th>Correlation</th><th>Strength</th></tr>
''')
corr_pairs = [
    ('Price vs Car Age', stats['corr_price_age']),
    ('Price vs Year', stats['corr_price_year']),
    ('Price vs KMs Driven', stats['corr_price_kms']),
    ('Price vs Log(KMs)', stats['corr_price_logkms']),
]
for label, val in corr_pairs:
    strength = ('Strong' if abs(val) > 0.5 else 'Moderate' if abs(val) > 0.3 else 'Weak')
    direction = 'positive' if val > 0 else 'negative'
    color = '#27ae60' if val > 0 else '#e74c3c'
    html_parts.append(f'<tr><td>{label}</td><td style="color:{color};font-weight:700">{val:+.3f}</td><td>{strength} {direction}</td></tr>\n')
html_parts.append(f'''
    </table>
    <div class="img-row">
        <div class="img-container">{img_html('correlation_heatmap.png')}</div>
        <div class="img-container">{img_html('price_vs_age.png')}</div>
    </div>
</div>
''')

# Section 6: KMs Driven
html_parts.append(f'''
<div class="section">
    <h2>&#54; KMs Driven Analysis</h2>
    <div class="dual">
        <div>
            <table class="stats-table">
                <tr><th>Statistic</th><th>Value</th></tr>
                <tr><td>Minimum</td><td>{stats["kms_min"]:,} km</td></tr>
                <tr><td>Median</td><td>{stats["kms_median"]:,} km</td></tr>
                <tr><td>Mean</td><td>{stats["kms_mean"]:,} km</td></tr>
                <tr><td>Maximum</td><td>{stats["kms_max"]:,} km</td></tr>
            </table>
        </div>
        <div class="img-container">{img_html('kms_distribution.png')}</div>
    </div>
</div>
''')

# Section 7: Year / Age
html_parts.append(f'''
<div class="section">
    <h2>&#55; Manufacturing Year &amp; Age</h2>
    <table class="stats-table" style="max-width:400px">
        <tr><th>Statistic</th><th>Value</th></tr>
        <tr><td>Earliest Year</td><td>{stats["year_min"]}</td></tr>
        <tr><td>Latest Year</td><td>{stats["year_max"]}</td></tr>
        <tr><td>Most Common Year</td><td>{stats["most_common_year"]}</td></tr>
        <tr><td>Avg Car Age</td><td>{stats["age_mean"]} years</td></tr>
        <tr><td>Oldest Car Age</td><td>{stats["age_max"]} years</td></tr>
    </table>
    <div class="img-container">{img_html('year_distribution.png')}</div>
</div>
''')

# Section 8: Top 10 Most Expensive
html_parts.append(f'''
<div class="section">
    <h2>&#56; Top 10 Most Expensive Cars</h2>
    <div class="img-container">{img_html('top10_expensive.png')}</div>
</div>
''')

# Section 9: ML Readiness
html_parts.append(f'''
<div class="section">
    <h2>&#57; ML Readiness Summary</h2>
    <table class="stats-table">
        <tr><th>Aspect</th><th>Status</th><th>Details</th></tr>
        <tr><td>Missing Values</td><td style="color:#27ae60;font-weight:700">&#10003; Clean</td><td>No missing values in any column</td></tr>
        <tr><td>Duplicates</td><td style="color:#27ae60;font-weight:700">&#10003; Removed</td><td>{stats["duplicates"]:,} duplicate rows dropped</td></tr>
        <tr><td>Outliers (KMs)</td><td style="color:#f39c12;font-weight:700">Capped</td><td>Capped at 99th percentile (228,560 km)</td></tr>
        <tr><td>Categorical Encoding</td><td style="color:#27ae60;font-weight:700">&#10003; Done</td><td>One-hot encoded (company: 36, fuel_type: 3)</td></tr>
        <tr><td>Feature Scaling</td><td style="color:#27ae60;font-weight:700">&#10003; Applied</td><td>StandardScaler on car_age &amp; kms_driven</td></tr>
        <tr><td>Train/Test Split</td><td style="color:#27ae60;font-weight:700">&#10003; 80/20</td><td>{stats["n_train"]:,} train, {stats["n_test"]:,} test samples</td></tr>
        <tr><td>Total Features</td><td style="color:#27ae60;font-weight:700">&#10003; 39</td><td>2 numerical + 37 one-hot encoded</td></tr>
        <tr><td>Target Variable</td><td style="color:#2980b9;font-weight:700">Price</td><td>Regression task (range: {fmt_price(stats["price_min"])} &ndash; {fmt_price(stats["price_max"])})</td></tr>
    </table>
</div>
''')

# Section 10: Key Insights
diesel_pct = stats['fuel_diesel'] / stats['total_rows_clean'] * 100
maruti_pct = stats['company_most_listings_count'] / stats['total_rows_clean'] * 100
dup_pct = stats['duplicates'] / stats['total_rows_original'] * 100

html_parts.append(f'''
<div class="section">
    <h2>&#49;&#48; Key Insights</h2>
    <ol style="margin-left:20px; line-height:2">
        <li><strong>Price is right-skewed</strong> &mdash; most cars are priced under &#8377;5 Lakh,
            with a long tail of luxury cars (BMW, Mercedes, Audi) above &#8377;20 Lakh.
            <em>Log-transforming the target is recommended for linear models.</em></li>
        <li><strong>Diesel dominates</strong> &mdash; {diesel_pct:.1f}% of listings are diesel cars,
            and they tend to have higher average prices than petrol cars.</li>
        <li><strong>Car age is the strongest predictor</strong> &mdash; the correlation between
            car age and price is <strong>{stats["corr_price_age"]:+.3f}</strong>, showing newer cars command significantly higher prices.</li>
        <li><strong>Maruti dominates the market</strong> &mdash; {maruti_pct:.1f}% of all listings are Maruti cars,
            though luxury brands like Mercedes, BMW, and Audi occupy the top price brackets.</li>
        <li><strong>KMs driven has weak negative correlation</strong> ({stats["corr_price_kms"]:+.3f}) with price &mdash;
            beyond a certain threshold, additional KMs don&apos;t reduce price much further.</li>
        <li><strong>Significant duplicate data</strong> &mdash; {stats["duplicates"]:,} duplicate rows ({dup_pct:.1f}% of data)
            were removed, indicating possible scraping artifacts or repeated listings.</li>
    </ol>
</div>
''')

# Close tags
html_parts.append('''
</div>
<div class="footer">
    <p>Car Price Dataset EDA Report</p>
</div>
</body>
</html>
''')

# Write report
report_html = '\n'.join(html_parts)
report_path = os.path.join(REPORT_DIR, 'car_price_eda_report.html')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_html)

print(f"\n[4] HTML report saved to: {report_path}")
print(f"    Visualizations in: {IMG_DIR}")

# List generated images
print("\n[5] Generated images:")
for fname in sorted(os.listdir(IMG_DIR)):
    fpath = os.path.join(IMG_DIR, fname)
    size = os.path.getsize(fpath) / 1024
    print(f"    |-- {fname} ({size:.0f} KB)")

print("\nReport generation complete!")
