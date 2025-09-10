import streamlit as st
import pandas as pd
import os
from src.collect import collect_products

st.set_page_config(page_title="Amazon Supplements Trends", layout="wide")

st.title("Amazon Best-Selling Supplements & Vitamins")

# Sidebar
st.sidebar.header("Controls")
max_pages = st.sidebar.slider("Number of Pages to Scrape", 1, 5, 2)
refresh = st.sidebar.button("Scrape Again")

# Data file path
data_file = "data/latest_amazon_supplements.csv"
df = None

# --- Always scrape at startup ---
st.info("🔄 Scraping fresh data on startup, please wait...")
df = collect_products(max_pages=max_pages)
os.makedirs("data", exist_ok=True)

if df is not None and not df.empty:
    df.to_csv(data_file, index=False, encoding="utf-8")
    st.success(f"✅ Scraped {len(df)} products and saved to {data_file}")
else:
    st.error("❌ Scraping failed — no products found. Try again.")

# --- Manual refresh from sidebar ---
if refresh:
    st.info("🔄 Scraping latest data, please wait...")
    df = collect_products(max_pages=max_pages)
    if df is not None and not df.empty:
        df.to_csv(data_file, index=False, encoding="utf-8")
        st.success(f"✅ Scraped {len(df)} products and saved to {data_file}")
    else:
        st.error("❌ Scraping failed — no products found. Try again.")

if os.path.exists(data_file):
    # Read CSV correctly using the first row as header
    df = pd.read_csv(data_file, header=0)  # <-- make sure header=0
    # Reset index to start at 1
    df.index = range(1, len(df) + 1)

# --- Display results ---
if df is not None and not df.empty:

    st.subheader("Top Products")
    st.dataframe(df)

    st.subheader("Price Distribution")
    df["price_clean"] = (
        df["Price"]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
        .astype(float)
        .fillna(0)
    )

    if df["price_clean"].sum() == 0:
        st.warning("⚠️ No valid price data to plot.")
    else:
        st.bar_chart(df.set_index("Title")["price_clean"].head(10))
else:
    st.warning("No data available. Please scrape again.")
