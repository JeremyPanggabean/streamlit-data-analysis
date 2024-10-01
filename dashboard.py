import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Function to load data
@st.cache_data
def load_data():
    df = pd.read_csv("all_dataset.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

# Main function
def main():
    st.title("🛍️ E-Commerce Analysis Dashboard")

    # Load data
    try:
        all_df = load_data()
        st.success("Data loaded successfully!")
    except FileNotFoundError:
        st.error("Please ensure 'all_dataset.csv' is in the same directory as this script.")
        return


    # Sidebar filters
    st.sidebar.header("Filters")

    # Add logo to sidebar
    st.sidebar.image("logo.jpg", width=250)

    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(all_df['order_purchase_timestamp'].min(), all_df['order_purchase_timestamp'].max()),
        min_value=all_df['order_purchase_timestamp'].min().date(),
        max_value=all_df['order_purchase_timestamp'].max().date()
    )

    # Filter data based on date range
    mask = (all_df['order_purchase_timestamp'].dt.date >= date_range[0]) & \
           (all_df['order_purchase_timestamp'].dt.date <= date_range[1])
    filtered_df = all_df[mask]

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", f"{len(filtered_df['order_id'].unique()):,}")
    with col2:
        st.metric("Total Revenue", f"${filtered_df['payment_value'].sum():,.2f}")
    with col3:
        st.metric("Unique Customers", f"{len(filtered_df['customer_id'].unique()):,}")
    with col4:
        st.metric("Average Order Value", f"${filtered_df['payment_value'].mean():,.2f}")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Product Categories", "Delivery Analysis", "Payment Analysis"])

    # Adjusting colors
    highlight_color = "#72BCD4"
    base_color = "#D3D3D3"


    with tab1:
        st.header("Top Product Categories")
        top_categories = filtered_df['product_category_name_english'].value_counts().nlargest(5)

        colors_tab1 = [highlight_color if i == 0 else base_color for i in range(len(top_categories))]

        fig = px.bar(
            x=top_categories.index,
            y=top_categories.values,
            title="Top 5 Product Categories by Sales",
            labels={'x': 'Product Category', 'y': 'Number of Sales'}
        )
        fig.update_traces(marker_color=colors_tab1)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Delivery Time Analysis")
        avg_delivery_time = filtered_df.groupby('customer_state')['delivery_time'].mean().nlargest(5)

        colors_tab2 = [highlight_color if i == 0 else base_color for i in range(len(avg_delivery_time))]

        fig = px.bar(
            x=avg_delivery_time.index,
            y=avg_delivery_time.values,
            title="Average Delivery Time by State",
            labels={'x': 'Customer State', 'y': 'Average Delivery Time (Days)'}
        )
        fig.update_traces(marker_color=colors_tab2)
        st.plotly_chart(fig, use_container_width=True)

    with ((((tab3)))):
        st.header("Payment Analysis")
        cancellation_rate = filtered_df[filtered_df['order_status'] == 'canceled'].groupby('payment_type').size() / \
                            filtered_df.groupby('payment_type').size() * 100

        max_value = cancellation_rate.max()
        colors_tab3 = [highlight_color if val == max_value else base_color for val in cancellation_rate.values]

        fig = px.bar(
            x=cancellation_rate.index,
            y=cancellation_rate.values,
            title="Order Cancellation Rate by Payment Method",
            labels={'x': 'Payment Method', 'y': 'Cancellation Rate (%)'}
        )
        fig.update_traces(marker_color=colors_tab3)
        st.plotly_chart(fig, use_container_width=True)

    # RFM Analysis
    st.header("RFM Analysis")

    # Calculate RFM metrics
    rfm_df = filtered_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    recent_date = filtered_df["order_purchase_timestamp"].max()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days

    # Create columns for RFM metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top Customers by Recency")
        recency_df = rfm_df.nsmallest(5, 'recency')[['customer_id', 'recency']]
        recency_df = recency_df.reset_index(drop=True)
        st.dataframe(recency_df, use_container_width=True)

    with col2:
        st.subheader("Top Customers by Frequency")
        frequency_df = rfm_df.nlargest(5, 'frequency')[['customer_id', 'frequency']]
        frequency_df = frequency_df.reset_index(drop=True)
        st.dataframe(frequency_df, use_container_width=True)

    with col3:
        st.subheader("Top Customers by Monetary")
        monetary_df = rfm_df.nlargest(5, 'monetary')[['customer_id', 'monetary']]
        monetary_df['monetary'] = monetary_df['monetary'].round(2)
        monetary_df = monetary_df.reset_index(drop=True)
        st.dataframe(monetary_df, use_container_width=True)

    # Additional RFM Visualizations
    st.subheader("RFM Distribution")
    rfm_metrics_col1, rfm_metrics_col2, rfm_metrics_col3 = st.columns(3)

    with rfm_metrics_col1:
        fig_recency = px.histogram(rfm_df, x="recency", title="Recency Distribution")
        fig_recency.update_traces(marker_color=highlight_color)
        st.plotly_chart(fig_recency, use_container_width=True)

    with rfm_metrics_col2:
        fig_frequency = px.histogram(rfm_df, x="frequency", title="Frequency Distribution")
        fig_frequency.update_traces(marker_color=highlight_color)
        st.plotly_chart(fig_frequency, use_container_width=True)

    with rfm_metrics_col3:
        fig_monetary = px.histogram(rfm_df, x="monetary", title="Monetary Distribution")
        fig_monetary.update_traces(marker_color=highlight_color)
        st.plotly_chart(fig_monetary, use_container_width=True)

if __name__ == "__main__":
    main()
