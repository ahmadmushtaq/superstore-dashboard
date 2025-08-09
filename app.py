import pandas as pd
import streamlit as sl
import matplotlib.pyplot as plt

df = pd.read_csv('data/superstore_dataset.csv', encoding="ISO-8859-1")

df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Year-Month'] = df['Order Date'].dt.to_period('M')

sl.set_page_config(page_title="Superstore Dashboard", layout='wide')
sl.title("Superstore Sales Dashbaord")
sl.markdown("Analyze sales trends, product proformance, and regional distribution")

years = sorted(df['Year'].unique())
months = sorted(df['Month'].unique())
regions = sorted(df['Region'].unique())
selected_year = sl.sidebar.selectbox("Select Year", years, index=0)

selected_region = sl.sidebar.multiselect(
    "Select Region(s)",
    regions,
    default=['East']  # All pre-selected
)


filtered_df = df[(df['Year'] == selected_year) & (df['Region'].isin(selected_region))]

total_sales = filtered_df['Sales'].sum()
total_orders = filtered_df['Order ID'].nunique()
average_order_value = total_sales / total_orders if total_orders else 0

monthly_sales = filtered_df.groupby('Year-Month')['Sales'].sum().reset_index()
monthly_sales['Year-Month'] = monthly_sales['Year-Month'].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly_sales['Year-Month'], monthly_sales['Sales'], marker = "o", linestyle = "-")
ax.set_title(f"Monthly Sales Trend for {selected_year}")
ax.set_xlabel("Year-Month")
ax.set_ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()


top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(5).reset_index()
top_products['Short Name'] = top_products['Product Name'].str.slice(0, 20) + '...'
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.barh(top_products['Short Name'], top_products['Sales'], color='skyblue')
ax2.set_xlabel("Total Sales")
ax2.set_title("Top 5 Products")
plt.tight_layout()
ax2.tick_params(axis='y', labelsize=8)



    


tab1, tab2, tab3, tab4 = sl.tabs(["Home","Monthlyh Sales","Top Products","Sales by Region"])
with tab1:
    sl.subheader(f"Year: {selected_year} | Regions: {', '.join(selected_region)}")
    col1, col2, col3 = sl.columns(3)
    col1.metric("Total Sales", f"{total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders}")
    col3.metric("Avg Order Value", f"{average_order_value:,.2f}")
    with sl.expander("🔍 View Filtered Data"):
        sl.dataframe(filtered_df.head(50))
with tab2:
    sl.subheader("Monthly Sales Trend")
    sl.pyplot(fig)
with tab3:
    sl.subheader("Top 5 Products by Sales")
    sl.pyplot(fig2)
with tab4:
    sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    col1, col2 = sl.columns([1, 2])
    with col1:
        fig3, ax3 = plt.subplots(figsize=(4, 4))
        ax3.pie(sales_by_region['Sales'], labels=sales_by_region['Region'], autopct='%1.1f%%', startangle=90,  textprops={'fontsize': 8})
        ax3.set_title("Sales by Region")
        plt.tight_layout()
        sl.subheader("Sales by Region")
        sl.pyplot(fig3)