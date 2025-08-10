import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px


@st.cache_data
def load_data():
    df = pd.read_csv('data/superstore_dataset.csv', encoding="ISO-8859-1")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Year-Month'] = df['Order Date'].dt.to_period('M')
    return df

st.set_page_config(page_title="Superstore Dashboard", layout='wide')
st.title("Superstore Sales Dashbaord")
st.markdown("Analyze sales trends, product proformance, and regional distribution")

df = load_data()

years = sorted(df['Year'].unique())
months = sorted(df['Month'].unique())
regions = sorted(df['Region'].unique())
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", years, index=0)

year_min = pd.Timestamp(f"{selected_year}-01-01")
year_max = pd.Timestamp(f"{selected_year}-12-31")

date_range = st.sidebar.date_input(
    "Select Date Rangge",
    value = [year_min, year_max],
    min_value=year_min,
    max_value=year_max,
)

selected_region = st.sidebar.multiselect(
    "Select Region(s)",
    regions,
    default=['East']  
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df['Order Date'] >= pd.to_datetime(start_date)) 
        & (df['Order Date'] <= pd.to_datetime(end_date))
        & (df['Region'].isin(selected_region))
        ]
else:
    filtered_df = df[
        (df['Order Date'] >= pd.to_datetime(year_min)) 
        & (df['Order Date'] <= pd.to_datetime(year_max))
        & (df['Region'].isin(selected_region))
        ]

categories = df['Category'].unique()
selected_categories = st.sidebar.multiselect("Select Categories", categories)

# Sub-Category filter (based on selected categories)
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    subcategories = filtered_df['Sub-Category'].unique()
else:
    subcategories = list(df['Sub-Category'].unique())
selected_subcategories = st.sidebar.multiselect("Select Sub-Categories", subcategories)
if selected_subcategories:
    filtered_df = filtered_df[filtered_df['Sub-Category'].isin(selected_subcategories)]

total_sales = filtered_df['Sales'].sum()
total_orders = filtered_df['Order ID'].nunique()
average_order_value = total_sales / total_orders if total_orders else 0

monthly_sales = filtered_df.groupby('Year-Month')['Sales'].sum().reset_index()
monthly_sales['Year-Month'] = monthly_sales['Year-Month'].dt.to_timestamp()


top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(5).reset_index()
top_products['Short Name'] = top_products['Product Name'].str.slice(0, 20) + '...'
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.barh(top_products['Short Name'], top_products['Sales'], color='skyblue')
ax2.set_xlabel("Total Sales")
ax2.set_title("Top 5 Products")
plt.tight_layout()
ax2.tick_params(axis='y', labelsize=8)

tab1, tab2, tab3, tab4 = st.tabs(["Home","Monthly Sales","Top Products","Sales by Region"])

with tab1:
    st.subheader(f"Year: {selected_year} | Regions: {', '.join(selected_region)}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"{total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders}")
    col3.metric("Avg Order Value", f"{average_order_value:,.2f}")
    with st.expander("🔍 View Filtered Data"):
        st.dataframe(filtered_df.head(50))

with tab2:
    st.subheader("Monthly Sales Trend")
    fig = px.line(
        monthly_sales,
        x='Year-Month',
        y='Sales',
        markers=True
        )
    fig.update_layout(
        xaxis_title='Year-Month',
        yaxis_title='Total Sales',
        hovermode='x unified'
        )
    fig.update_xaxes(
        dtick="M1", 
        tickformat="%b %Y" 
        )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Top 5 Products by Sales")
    st.pyplot(fig2)

with tab4:
    sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    col1, col2 = st.columns([1, 2])
    with col1:
        fig3, ax3 = plt.subplots(figsize=(4, 4))
        ax3.pie(sales_by_region['Sales'], labels=sales_by_region['Region'], autopct='%1.1f%%', startangle=90,  textprops={'fontsize': 8})
        ax3.set_title("Sales by Region")
        plt.tight_layout()
        st.subheader("Sales by Region")
        st.pyplot(fig3)
