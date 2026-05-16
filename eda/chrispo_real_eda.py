#!/usr/bin/env python3
"""
============================================================
  Chrispo E.P.O LTD — Real Estate & Short-Stay Analytics
  Author  : Frederick Opoku Afriyie
  Locations: Barekese (Kumasi) · Buokrom (Kumasi) ·
             Offinso · Amrahia (Accra)
  Regions : Ashanti Region · Greater Accra Region
============================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#FAFBFF",
    "axes.facecolor":   "#FAFBFF",
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   12,
    "axes.titleweight": "bold",
    "axes.labelsize":   10,
})

BLUE    = "#1A3A6B"
GOLD    = "#C9A84C"
RED     = "#C0392B"
GREEN   = "#27AE60"
LIGHT   = "#EBF0FA"
GREY    = "#7F8C8D"

fmt_ghs = lambda x, _: f"₵{x/1000:.0f}K" if x >= 1000 else f"₵{x:.0f}"
fmt_pct = lambda x, _: f"{x:.0f}%"

# ── Load ───────────────────────────────────────────────────────
df_b = pd.read_csv("/home/claude/chrispo_bookings_data.csv", parse_dates=["Check_In_Date"])
df_l = pd.read_csv("/home/claude/chrispo_listings_data.csv", parse_dates=["Listing_Date"])
df_p = pd.read_csv("/home/claude/chrispo_pricing_journey.csv")

print(f"Bookings:  {len(df_b)} records  |  Listings: {len(df_l)}  |  Pricing phases: {len(df_p)}")

# ════════════════════════════════════════════════════════════════
# FIGURE 1 — PRICING JOURNEY: Barekese & Buokrom
# The core story: started too high → data-driven repricing → growth
# ════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle(
    "Chrispo E.P.O LTD — Pricing Journey: Short-Stay & AirBnB Properties",
    fontsize=15, fontweight="bold", color=BLUE, y=1.01
)

PHASE_COLORS = {
    "Phase 1 – Launch (Overpriced)":          RED,
    "Phase 2 – First Adjustment":             GOLD,
    "Phase 2 – Market Research Adjustment":   GOLD,
    "Phase 3 – Optimised Pricing":            GREEN,
    "Phase 3 – Optimised":                    GREEN,
    "Phase 4 – Stable Growth":                BLUE,
}

# 1a — Barekese occupancy per phase
bar_p = df_p[df_p["Property"]=="Barekese"].copy()
colors_bar = [PHASE_COLORS.get(p, GREY) for p in bar_p["Phase"]]
bars = axes[0,0].bar(range(len(bar_p)), bar_p["Occupancy_Rate_Pct"],
                      color=colors_bar, edgecolor="white", linewidth=1.5)
axes[0,0].set_xticks(range(len(bar_p)))
axes[0,0].set_xticklabels([f"Ph {i+1}" for i in range(len(bar_p))], fontsize=9)
axes[0,0].set_title("Barekese — Occupancy Rate by Phase")
axes[0,0].set_ylabel("Occupancy Rate (%)")
axes[0,0].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_pct))
for bar, v in zip(bars, bar_p["Occupancy_Rate_Pct"]):
    axes[0,0].text(bar.get_x()+bar.get_width()/2, v+0.8, f"{v:.0f}%",
                   ha="center", fontsize=9, fontweight="bold")

# 1b — Barekese: weekday rate journey
axes[0,1].plot(range(len(bar_p)), bar_p["Weekday_Rate_GHS"], marker="o",
               color=RED, linewidth=2.5, markersize=9, label="Weekday Rate")
axes[0,1].plot(range(len(bar_p)), bar_p["Weekend_Rate_GHS"], marker="s",
               color=BLUE, linewidth=2.5, markersize=9, linestyle="--", label="Weekend Rate")
axes[0,1].fill_between(range(len(bar_p)), bar_p["Weekday_Rate_GHS"], alpha=0.1, color=RED)
axes[0,1].set_xticks(range(len(bar_p)))
axes[0,1].set_xticklabels([f"Ph {i+1}" for i in range(len(bar_p))], fontsize=9)
axes[0,1].set_title("Barekese — Nightly Rate Journey (GHS)")
axes[0,1].set_ylabel("Rate (GHS)")
axes[0,1].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[0,1].legend(fontsize=9)
# Annotate the drop
axes[0,1].annotate("Price reduced\nto drive bookings",
                    xy=(1, bar_p["Weekday_Rate_GHS"].iloc[1]),
                    xytext=(1.6, bar_p["Weekday_Rate_GHS"].iloc[0]+50),
                    arrowprops=dict(arrowstyle="->", color=RED),
                    fontsize=8, color=RED)

# 1c — Barekese: est monthly revenue per phase
bars2 = axes[0,2].bar(range(len(bar_p)), bar_p["Est_Monthly_Revenue_GHS"],
                       color=colors_bar, edgecolor="white", linewidth=1.5)
axes[0,2].set_xticks(range(len(bar_p)))
axes[0,2].set_xticklabels([f"Ph {i+1}" for i in range(len(bar_p))], fontsize=9)
axes[0,2].set_title("Barekese — Est. Monthly Revenue (GHS)")
axes[0,2].set_ylabel("Revenue (GHS)")
axes[0,2].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
for bar, v in zip(bars2, bar_p["Est_Monthly_Revenue_GHS"]):
    axes[0,2].text(bar.get_x()+bar.get_width()/2, v+200, fmt_ghs(v, None),
                   ha="center", fontsize=8, fontweight="bold")

# legend patches
legend_patches = [
    mpatches.Patch(color=RED,   label="Phase 1: Overpriced"),
    mpatches.Patch(color=GOLD,  label="Phase 2: Adjusted"),
    mpatches.Patch(color=GREEN, label="Phase 3: Optimised"),
    mpatches.Patch(color=BLUE,  label="Phase 4: Growth"),
]
axes[0,2].legend(handles=legend_patches, fontsize=7, loc="upper left")

# 1d — Buokrom occupancy per phase
buo_p = df_p[df_p["Property"]=="Buokrom"].copy()
colors_buo = [PHASE_COLORS.get(p, GREY) for p in buo_p["Phase"]]
bars3 = axes[1,0].bar(range(len(buo_p)), buo_p["Occupancy_Rate_Pct"],
                       color=colors_buo, edgecolor="white", linewidth=1.5)
axes[1,0].set_xticks(range(len(buo_p)))
axes[1,0].set_xticklabels([f"Ph {i+1}" for i in range(len(buo_p))], fontsize=9)
axes[1,0].set_title("Buokrom AirBnB — Occupancy Rate by Phase")
axes[1,0].set_ylabel("Occupancy Rate (%)")
axes[1,0].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_pct))
for bar, v in zip(bars3, buo_p["Occupancy_Rate_Pct"]):
    axes[1,0].text(bar.get_x()+bar.get_width()/2, v+0.8, f"{v:.0f}%",
                   ha="center", fontsize=9, fontweight="bold")

# 1e — Buokrom rate journey
axes[1,1].plot(range(len(buo_p)), buo_p["Weekday_Rate_GHS"], marker="o",
               color=RED, linewidth=2.5, markersize=9, label="Weekday Rate")
axes[1,1].plot(range(len(buo_p)), buo_p["Weekend_Rate_GHS"], marker="s",
               color=BLUE, linewidth=2.5, markersize=9, linestyle="--", label="Weekend Rate")
axes[1,1].fill_between(range(len(buo_p)), buo_p["Weekday_Rate_GHS"], alpha=0.1, color=RED)
axes[1,1].set_xticks(range(len(buo_p)))
axes[1,1].set_xticklabels([f"Ph {i+1}" for i in range(len(buo_p))], fontsize=9)
axes[1,1].set_title("Buokrom AirBnB — Nightly Rate Journey (GHS)")
axes[1,1].set_ylabel("Rate (GHS)")
axes[1,1].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[1,1].legend(fontsize=9)

# 1f — Buokrom monthly revenue
bars4 = axes[1,2].bar(range(len(buo_p)), buo_p["Est_Monthly_Revenue_GHS"],
                       color=colors_buo, edgecolor="white", linewidth=1.5)
axes[1,2].set_xticks(range(len(buo_p)))
axes[1,2].set_xticklabels([f"Ph {i+1}" for i in range(len(buo_p))], fontsize=9)
axes[1,2].set_title("Buokrom AirBnB — Est. Monthly Revenue (GHS)")
axes[1,2].set_ylabel("Revenue (GHS)")
axes[1,2].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
for bar, v in zip(bars4, buo_p["Est_Monthly_Revenue_GHS"]):
    axes[1,2].text(bar.get_x()+bar.get_width()/2, v+150, fmt_ghs(v, None),
                   ha="center", fontsize=8, fontweight="bold")
buo_legend = [
    mpatches.Patch(color=RED,   label="Phase 1: Overpriced"),
    mpatches.Patch(color=GOLD,  label="Phase 2: Benchmarked"),
    mpatches.Patch(color=GREEN, label="Phase 3: Optimised"),
]
axes[1,2].legend(handles=buo_legend, fontsize=7, loc="upper left")

plt.tight_layout()
plt.savefig("/home/claude/fig1_pricing_journey.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Figure 1 saved: fig1_pricing_journey.png")

# ════════════════════════════════════════════════════════════════
# FIGURE 2 — BOOKING PERFORMANCE (Barekese & Buokrom)
# ════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle(
    "Chrispo E.P.O LTD — Booking Performance: Barekese & Buokrom",
    fontsize=15, fontweight="bold", color=BLUE, y=1.01
)

stays = df_b[df_b["Booking_Type"]=="Nightly Stay"].copy()

# 2a — Monthly bookings: Barekese
bar_monthly = (stays[stays["Property"]=="Barekese"]
               .groupby(["Year","Month","Check_In_Date"])
               .size().reset_index(name="count"))
bar_monthly["YM"] = bar_monthly["Check_In_Date"].dt.to_period("M")
bar_rev = (stays[stays["Property"]=="Barekese"]
           .groupby(stays[stays["Property"]=="Barekese"]["Check_In_Date"].dt.to_period("M"))["Revenue_GHS"]
           .sum().reset_index())
bar_rev.columns = ["YM","Revenue_GHS"]
bar_rev["YM_str"] = bar_rev["YM"].astype(str)
step = max(1, len(bar_rev)//8)
axes[0,0].bar(range(len(bar_rev)), bar_rev["Revenue_GHS"], color=BLUE, alpha=0.8, edgecolor="white")
axes[0,0].set_xticks(range(0, len(bar_rev), step))
axes[0,0].set_xticklabels(bar_rev["YM_str"].iloc[::step], rotation=45, ha="right", fontsize=8)
axes[0,0].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[0,0].set_title("Barekese — Monthly Revenue (GHS)")
axes[0,0].set_ylabel("Revenue (GHS)")

# 2b — Barekese: weekday vs weekend revenue
wkd = stays[stays["Property"]=="Barekese"].groupby("Is_Weekend")["Revenue_GHS"].sum()
labels = ["Weekday", "Weekend"]
axes[0,1].bar(labels, [wkd.get(False,0), wkd.get(True,0)],
              color=[BLUE, GOLD], edgecolor="white", linewidth=1.5)
axes[0,1].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[0,1].set_title("Barekese — Weekday vs Weekend Revenue")
axes[0,1].set_ylabel("Total Revenue (GHS)")
for i, v in enumerate([wkd.get(False,0), wkd.get(True,0)]):
    axes[0,1].text(i, v+500, fmt_ghs(v,None), ha="center", fontweight="bold")

# 2c — Barekese: booking type split (stays vs events)
bar_all = df_b[df_b["Property"]=="Barekese"]
type_rev = bar_all.groupby("Booking_Type")["Revenue_GHS"].sum()
axes[0,2].pie(type_rev, labels=type_rev.index, autopct="%1.1f%%",
              colors=[BLUE, GOLD], startangle=140,
              wedgeprops={"edgecolor":"white","linewidth":2})
axes[0,2].set_title("Barekese — Revenue Split\n(Stays vs Events)")

# 2d — Buokrom monthly revenue
buo_rev = (stays[stays["Property"]=="Buokrom"]
           .groupby(stays[stays["Property"]=="Buokrom"]["Check_In_Date"].dt.to_period("M"))["Revenue_GHS"]
           .sum().reset_index())
buo_rev.columns = ["YM","Revenue_GHS"]
buo_rev["YM_str"] = buo_rev["YM"].astype(str)
step2 = max(1, len(buo_rev)//8)
axes[1,0].bar(range(len(buo_rev)), buo_rev["Revenue_GHS"], color=GREEN, alpha=0.85, edgecolor="white")
axes[1,0].set_xticks(range(0, len(buo_rev), step2))
axes[1,0].set_xticklabels(buo_rev["YM_str"].iloc[::step2], rotation=45, ha="right", fontsize=8)
axes[1,0].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[1,0].set_title("Buokrom AirBnB — Monthly Revenue (GHS)")
axes[1,0].set_ylabel("Revenue (GHS)")

# 2e — Phase revenue comparison side by side
phase_rev = df_b.groupby(["Property","Pricing_Phase"])["Revenue_GHS"].sum().unstack(level=0)
x = range(len(phase_rev))
w = 0.35
p1 = phase_rev.get("Barekese", pd.Series([0]*len(phase_rev))).fillna(0)
p2 = phase_rev.get("Buokrom",  pd.Series([0]*len(phase_rev))).fillna(0)
axes[1,1].bar([i-w/2 for i in x], p1, width=w, color=BLUE, label="Barekese", alpha=0.85)
axes[1,1].bar([i+w/2 for i in x], p2, width=w, color=GREEN, label="Buokrom", alpha=0.85)
phase_labels = [f"Ph{i+1}" for i in range(len(phase_rev))]
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels(phase_labels, fontsize=9)
axes[1,1].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[1,1].set_title("Total Revenue by Pricing Phase")
axes[1,1].set_ylabel("Revenue (GHS)")
axes[1,1].legend()

# 2f — Occupancy Rate trend: price down = occupancy up
occ_line = df_p[["Property","Phase","Occupancy_Rate_Pct"]].copy()
bar_occ = occ_line[occ_line["Property"]=="Barekese"]
buo_occ = occ_line[occ_line["Property"]=="Buokrom"]
axes[1,2].plot(range(len(bar_occ)), bar_occ["Occupancy_Rate_Pct"],
               marker="o", color=BLUE, linewidth=2.5, markersize=10, label="Barekese")
axes[1,2].plot(range(len(buo_occ)), buo_occ["Occupancy_Rate_Pct"],
               marker="s", color=GREEN, linewidth=2.5, markersize=10, linestyle="--", label="Buokrom")
axes[1,2].fill_between(range(len(bar_occ)), bar_occ["Occupancy_Rate_Pct"], alpha=0.08, color=BLUE)
axes[1,2].fill_between(range(len(buo_occ)), buo_occ["Occupancy_Rate_Pct"], alpha=0.08, color=GREEN)
axes[1,2].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_pct))
axes[1,2].set_title("Occupancy Rate Growth Across Phases")
axes[1,2].set_ylabel("Occupancy (%)")
axes[1,2].set_xlabel("Pricing Phase")
axes[1,2].legend()
axes[1,2].annotate("Repricing\ndrives growth", xy=(1, bar_occ["Occupancy_Rate_Pct"].iloc[1]),
                    xytext=(1.5, bar_occ["Occupancy_Rate_Pct"].iloc[1]-12),
                    arrowprops=dict(arrowstyle="->", color=RED), fontsize=8, color=RED)

plt.tight_layout()
plt.savefig("/home/claude/fig2_booking_performance.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Figure 2 saved: fig2_booking_performance.png")

# ════════════════════════════════════════════════════════════════
# FIGURE 3 — OFFINSO & AMRAHIA: Property Listings Analysis
# ════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle(
    "Chrispo E.P.O LTD — Offinso & Amrahia: Real Estate Portfolio",
    fontsize=15, fontweight="bold", color=BLUE, y=1.01
)

STATUS_COLORS = {"Sold": GREEN, "Available": BLUE, "Rented": GOLD, "Under Offer": GREY}

# 3a — Listings by location and status
loc_status = df_l.groupby(["Location","Status"]).size().unstack(fill_value=0)
loc_status.plot(kind="bar", ax=axes[0,0],
                color=[STATUS_COLORS.get(c, GREY) for c in loc_status.columns],
                edgecolor="white", linewidth=1.2)
axes[0,0].set_title("Listings by Location & Status")
axes[0,0].set_ylabel("Count")
axes[0,0].set_xlabel("")
axes[0,0].tick_params(axis="x", rotation=0)
axes[0,0].legend(title="Status", fontsize=8)

# 3b — Property type split
type_counts = df_l.groupby(["Location","Property_Type"]).size().unstack(fill_value=0)
type_counts.plot(kind="bar", ax=axes[0,1],
                 color=[BLUE, GOLD, GREEN],
                 edgecolor="white", linewidth=1.2)
axes[0,1].set_title("Property Type Mix by Location")
axes[0,1].set_ylabel("Count")
axes[0,1].set_xlabel("")
axes[0,1].tick_params(axis="x", rotation=0)
axes[0,1].legend(title="Type", fontsize=8)

# 3c — Price distribution by location (sale/rent)
for_sale = df_l[df_l["Rent_Type"].isna() & df_l["Property_Type"].isin(["House","Land"])]
locs = for_sale["Location"].unique()
price_data = [for_sale[for_sale["Location"]==l]["Price_GHS"] for l in locs]
bp = axes[0,2].boxplot(price_data, labels=locs, patch_artist=True,
                        medianprops={"color": GOLD, "linewidth": 2.5})
[p.set_facecolor(BLUE) for p in bp["boxes"]]
[p.set_alpha(0.7) for p in bp["boxes"]]
axes[0,2].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[0,2].set_title("Sale Price Distribution by Location")
axes[0,2].set_ylabel("Price (GHS)")

# 3d — Total portfolio value by location
port_val = df_l.groupby("Location")["Price_GHS"].sum()
colors_loc = [BLUE, GOLD]
bars_port = axes[1,0].bar(port_val.index, port_val.values, color=colors_loc, edgecolor="white", linewidth=1.5)
axes[1,0].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[1,0].set_title("Total Portfolio Value by Location (GHS)")
axes[1,0].set_ylabel("Value (GHS)")
for bar, v in zip(bars_port, port_val.values):
    axes[1,0].text(bar.get_x()+bar.get_width()/2, v*1.01, fmt_ghs(v,None),
                   ha="center", fontsize=9, fontweight="bold")

# 3e — Listings by year
yr_loc = df_l.groupby(["Year","Location"]).size().unstack(fill_value=0)
yr_loc.plot(kind="bar", ax=axes[1,1], color=colors_loc, edgecolor="white", linewidth=1.2)
axes[1,1].set_title("New Listings per Year by Location")
axes[1,1].set_ylabel("Count")
axes[1,1].set_xlabel("Year")
axes[1,1].tick_params(axis="x", rotation=0)
axes[1,1].legend(title="Location", fontsize=9)

# 3f — Rent breakdown (monthly rent amounts)
rentals = df_l[df_l["Rent_Type"]=="monthly"].copy()
axes[1,2].barh(range(len(rentals)),
               rentals["Price_GHS"],
               color=[STATUS_COLORS.get(s, GREY) for s in rentals["Status"]],
               edgecolor="white")
labels_rent = [f"{r['Location']} · {r['Bedrooms']:.0f}BR" for _, r in rentals.iterrows()]
axes[1,2].set_yticks(range(len(rentals)))
axes[1,2].set_yticklabels(labels_rent, fontsize=8)
axes[1,2].xaxis.set_major_formatter(mticker.FuncFormatter(fmt_ghs))
axes[1,2].set_title("Monthly Rental Rates (GHS)\nby Unit")
axes[1,2].set_xlabel("Monthly Rent (GHS)")
legend_items = [mpatches.Patch(color=v, label=k) for k, v in STATUS_COLORS.items() if k != "Under Offer"]
axes[1,2].legend(handles=legend_items, fontsize=8)

plt.tight_layout()
plt.savefig("/home/claude/fig3_listings_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Figure 3 saved: fig3_listings_analysis.png")

# ════════════════════════════════════════════════════════════════
# KEY INSIGHTS
# ════════════════════════════════════════════════════════════════
bar_stays = df_b[df_b["Property"]=="Barekese"]
buo_stays = df_b[df_b["Property"]=="Buokrom"]
bar_ph1 = bar_stays[bar_stays["Pricing_Phase"].str.contains("Overpriced")]["Revenue_GHS"].sum()
bar_ph3 = bar_stays[bar_stays["Pricing_Phase"].str.contains("Optimised")]["Revenue_GHS"].sum()

print("\n" + "="*62)
print("  CHRISPO E.P.O LTD — KEY ANALYTICAL INSIGHTS")
print("="*62)
print(f"  Barekese total revenue (all phases) : GHS {bar_stays['Revenue_GHS'].sum():,.0f}")
print(f"  Buokrom total revenue (all phases)  : GHS {buo_stays['Revenue_GHS'].sum():,.0f}")
print(f"  Barekese Ph1 rev (overpriced)       : GHS {bar_ph1:,.0f}")
print(f"  Barekese Ph3 rev (optimised)        : GHS {bar_ph3:,.0f}")
print(f"  Revenue uplift from repricing       : +{((bar_ph3-bar_ph1)/bar_ph1*100):.0f}%")
print(f"  Barekese occupancy: Ph1→Ph3         : 18% → 58%")
print(f"  Buokrom occupancy: Ph1→Ph3          : 15% → 61%")
print(f"  Offinso total listings              : {len(df_l[df_l['Location']=='Offinso'])}")
print(f"  Amrahia total listings              : {len(df_l[df_l['Location']=='Amrahia'])}")
print(f"  Offinso portfolio value             : GHS {df_l[df_l['Location']=='Offinso']['Price_GHS'].sum():,.0f}")
print(f"  Amrahia portfolio value             : GHS {df_l[df_l['Location']=='Amrahia']['Price_GHS'].sum():,.0f}")
print("="*62)
print("\n✓ All figures generated.")
