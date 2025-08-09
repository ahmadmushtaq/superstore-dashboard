import pandas as pd
import streamlit as sl
import matplotlib as mp

df = pd.read_csv('data/superstore_dataset.csv', encoding="ISO-8859-1")

df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')
df.insert(df.columns.get_loc('Order Date')+1, 'Sale YM', df['Order Date'].dt.to_period('M'))
monthly_Sales = df.groupby('Sale YM')['Sales'].sum().reset_index()
product_sale = df.groupby('Product Name')['Sales'].sum()
product_sale = product_sale.sort_values(ascending=False)
region_sale = df.groupby('Region')['Sales'].sum()
region_sale = region_sale.sort_values(ascending=False)
print(region_sale)
