import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# layout config
st.set_page_config(page_title='Member Transaction Dashboard', layout='wide')

st.title(':bar_chart: Retailer Transaction Dashboard')
st.markdown("<style>div.block-container{padding-top:3rem;}</style>",unsafe_allow_html=True)

# Manually specify the CSV file path
file_path = 'E:\\Elevatoz intern\\5_Day\\Sample_Reports\\Transactions_sample.csv'

# Load data using pd.read_csv()
@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path)
    return df

df = load_data(file_path)


# Streamlit Sidebar - Filters
st.sidebar.header("Filter Data")
member_status = st.sidebar.multiselect("Select Member Status", df['memberStatus'].unique())
member_type = st.sidebar.multiselect("Select Member Type", df['memberType'].unique())
member_tier = st.sidebar.multiselect("Select Member Tier", df['memberTier'].unique())

# Add date range filter
st.sidebar.subheader("Select Date Range")
min_date = pd.to_datetime(df['transactionDate']).min()
max_date = pd.to_datetime(df['transactionDate']).max()
date_range = st.sidebar.date_input("Date Range", [min_date.to_pydatetime(), max_date.to_pydatetime()])

if len(date_range) == 2:
    start_date, end_date = date_range
    df['transactionDate'] = pd.to_datetime(df['transactionDate'])
    df = df[(df['transactionDate'] >= pd.Timestamp(start_date)) & (df['transactionDate'] <= pd.Timestamp(end_date))]

with st.expander("Data Preview"):
    st.dataframe(
        df,
        column_config={"Filtered data": st.column_config.NumberColumn(format="%d")},
    )

# Filter the DataFrame based on the selected options
filtered_df = df[
    df['memberStatus'].isin(member_status) & 
    df['memberType'].isin(member_type) & 
    df['memberTier'].isin(member_tier)
]

# Create columns for side-by-side plots
col1, col2, col3 = st.columns(3)

# Plot 1: Points Distribution by Member Tier
with col1:
    tier_points = filtered_df.groupby('memberTier')['memberPoints'].sum().reset_index()
    fig = px.bar(tier_points, x='memberTier', y='memberPoints', color='memberTier',
                 title='Points by Member Tier',
                 labels={'memberTier': 'Member Tier', 'memberPoints': 'Total Points'},
                 hover_data=['memberTier', 'memberPoints'])
    st.plotly_chart(fig, use_container_width=True)

# Plot 2: Transactions Over Time
with col2:
    filtered_df['transactionDate'] = pd.to_datetime(filtered_df['transactionDate'])
    transaction_over_time = filtered_df.groupby('transactionDate').size().reset_index(name='Number of Transactions')
    fig = px.line(transaction_over_time, x='transactionDate', y='Number of Transactions',
                  title='Transactions Over Time', 
                  labels={'transactionDate': 'Transaction Date', 'Number of Transactions': 'Transactions'},
                  hover_data=['transactionDate', 'Number of Transactions'])
    st.plotly_chart(fig, use_container_width=True)

# Plot 3: Points Distribution by Points Group
with col3:
    points_group = filtered_df.groupby('pointsGroup')['memberPoints'].sum().reset_index()
    fig = px.pie(points_group, names='pointsGroup', values='memberPoints', 
                 color_discrete_sequence=['lightgreen'],
                 title='Points by Points Group', 
                 hover_data=['pointsGroup', 'memberPoints'],
                 labels={'pointsGroup': 'Points Group', 'memberPoints': 'Total Points'})
    st.plotly_chart(fig, use_container_width=True)

# Create another set of columns for the next set of plots
col4, col5, col6 = st.columns(3)

# Plot 4: Correlation Heatmap
with col4:
    numerical_cols = ['memberPoints', 'transactionDate']  
    filtered_df['transactionDate'] = pd.to_datetime(filtered_df['transactionDate'], errors='coerce')

    # Correlation Matrix
    correlation_matrix = filtered_df[numerical_cols].corr()

    # Plotting Heatmap
    fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale=[[0, 'purple'], [1, 'pink']],
            hovertemplate="Correlation between %{x} and %{y}: %{z}<extra></extra>"  
    ))
    fig.update_layout(title='Correlation Heatmap')
    st.plotly_chart(fig, use_container_width=True)

# Plot 5: Scatter Plot - Member Points vs Transaction Date
with col5:
    filtered_df['transactionDate'] = pd.to_datetime(filtered_df['transactionDate'], errors='coerce')
    filtered_df['transactionDateNum'] = filtered_df['transactionDate'].astype(np.int64) // 10**9  # Unix timestamp

    fig = px.scatter(filtered_df, x='transactionDate', y='memberPoints', color='memberTier', 
                     title='Member Points vs Transaction Date', 
                     labels={'transactionDate': 'Transaction Date', 'memberPoints': 'Member Points'},
                     hover_data={'transactionDate': True, 'memberPoints': True, 'memberName': True, 'memberTier': True})
    st.plotly_chart(fig, use_container_width=True)

with col6:
    filtered_df['transactionDate'] = pd.to_datetime(filtered_df['transactionDate'], errors='coerce')

    # Limit data to the first 10,000 rows
    limited_df = filtered_df.head(10000)

    transactions_by_datetime = limited_df.groupby('transactionDate').size().reset_index(name='Number of Transactions')

    fig = px.bar(transactions_by_datetime, 
                 x='transactionDate', 
                 y='Number of Transactions', 
                 title='Transactions Over Time ',
                 labels={'transactionDate': 'Transaction Date & Time', 'Number of Transactions': 'Number of Transactions'},
                 hover_data={'transactionDate': True, 'Number of Transactions': True},
                 color='Number of Transactions')
    st.plotly_chart(fig, use_container_width=True)
