""" @bruin
name: streamlit_dashboard
type: python
depends:
    - gold.load_to_motherduck
description: "Upload raw Olist dataset from local storage to Cloudflare R2 (Bronze layer)."
@bruin """

import streamlit as st
import duckdb
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

st.set_page_config(
    page_title="Car SCM Data Dashboard",
    layout="wide"
)

load_dotenv()

@st.cache_resource
def get_db_connection():
    try:
        token = os.getenv("MOTHERDUCK_TOKEN")
        if not token:
            st.error("MOTHERDUCK_TOKEN not found in the .env file")
            st.stop()
            
        con = duckdb.connect(f'md:?motherduck_token={token}')
        return con
    except Exception as e:
        st.error(f"MotherDuck connection error: {e}")
        st.stop()

con = get_db_connection()

# ==========================================
# PAGE 1 QUERIES (Sales Overview)
# ==========================================

@st.cache_data(ttl=600)
def get_highest_sales_car():
    query = """
        SELECT 
            p.CarMaker,
            p.CarModel,
            SUM(CAST(f.Quantity AS DOUBLE)) AS Total_Quantity_Sold
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_product p ON f.ProductID = p.ProductID
        GROUP BY p.CarMaker, p.CarModel
        ORDER BY Total_Quantity_Sold DESC
        LIMIT 1;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def average_sales():
    query = """
        SELECT 
            SUM(CAST(Sales AS DOUBLE)) / NULLIF(COUNT(DISTINCT OrderID), 0) AS Average_Order_Value
        FROM scm_db.main.fact_sales;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def sales_per_car():
    query = """
        SELECT 
            p.car_type,
            AVG(CAST(f.Sales AS DOUBLE)) AS Average_Revenue_Per_Transaction
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_product p ON f.ProductID = p.ProductID
        GROUP BY p.car_type
        ORDER BY Average_Revenue_Per_Transaction DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def revenue_per_month():
    query = """
        SELECT 
            d.Year,
            d.Month,
            SUM(CAST(f.Sales AS DOUBLE)) AS Monthly_Revenue,
            COUNT(DISTINCT f.OrderID) AS Total_Orders
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_date d ON f.OrderDateKey = d.DateKey
        GROUP BY d.Year, d.Month
        ORDER BY d.Year DESC, d.Month DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def revenue_per_day():
    query = """
        SELECT 
            f.OrderDateKey AS Date,
            d.DayOfWeekName,
            SUM(CAST(f.Sales AS DOUBLE)) AS Daily_Revenue
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_date d ON f.OrderDateKey = d.DateKey
        GROUP BY f.OrderDateKey, d.DayOfWeekName
        ORDER BY f.OrderDateKey DESC
        LIMIT 30;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def revenue_per_credit():
    query = """
        SELECT 
            CreditCardType,
            SUM(CAST(Sales AS DOUBLE)) AS Total_Revenue,
            COUNT(DISTINCT OrderID) AS Total_Orders
        FROM scm_db.main.fact_sales
        WHERE CreditCardType IS NOT NULL
        GROUP BY CreditCardType
        ORDER BY Total_Revenue DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def revenue_per_carmodel():
    query = """
        SELECT 
            p.CarModel, 
            SUM(CAST(f.Sales AS DOUBLE)) AS Total_Revenue
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_product p ON f.ProductID = p.ProductID
        GROUP BY p.CarModel
        ORDER BY Total_Revenue DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def revenue_per_city():
    query = """
        SELECT 
            c.City, 
            SUM(CAST(f.Sales AS DOUBLE)) AS Total_Revenue
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_customer c ON f.CustomerID = c.CustomerID
        GROUP BY c.City
        ORDER BY Total_Revenue DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_revenue_by_supplier():
    query = """
        SELECT 
            s.SupplierName,
            SUM(CAST(f.Sales AS DOUBLE)) AS Total_Revenue,
            COUNT(DISTINCT f.OrderID) AS Total_Orders,
            SUM(CAST(f.Quantity AS DOUBLE)) AS Total_Units_Supplied
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_supplier s ON f.SupplierID = s.SupplierID
        GROUP BY s.SupplierName
        ORDER BY Total_Revenue DESC;
    """
    return con.execute(query).df()

# ==========================================
# PAGE 2 QUERIES (Customer Feedback)
# ==========================================

@st.cache_data(ttl=600)
def get_feedback_distribution():
    query = """
        SELECT 
            CustomerFeedback,
            COUNT(*) AS Total_Feedbacks,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS Percentage
        FROM scm_db.main.fact_sales
        WHERE CustomerFeedback IS NOT NULL
        GROUP BY CustomerFeedback
        ORDER BY 
            CASE CustomerFeedback
                WHEN 'Very Bad' THEN 1
                WHEN 'Bad' THEN 2
                WHEN 'Okay' THEN 3
                WHEN 'Good' THEN 4
                WHEN 'Very Good' THEN 5
            END;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_feedback_by_job_group():
    query = """
        SELECT 
            c.job_group,
            f.CustomerFeedback,
            COUNT(f.OrderID) AS Order_Count
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_customer c ON f.CustomerID = c.CustomerID
        GROUP BY c.job_group, f.CustomerFeedback
        ORDER BY c.job_group, Order_Count DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_revenue_by_feedback():
    query = """
        SELECT 
            CustomerFeedback,
            SUM(CAST(Sales AS DOUBLE)) AS Total_Revenue,
            AVG(CAST(Sales AS DOUBLE)) AS Average_Order_Value,
            AVG(CAST(Discount AS DOUBLE)) AS Average_Discount
        FROM scm_db.main.fact_sales
        WHERE CustomerFeedback IS NOT NULL
        GROUP BY CustomerFeedback
        ORDER BY Total_Revenue DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_negative_feedback_by_city():
    query = """
        SELECT 
            c.City,
            COUNT(CASE WHEN f.CustomerFeedback IN ('Bad', 'Very Bad') THEN 1 END) AS Negative_Feedbacks,
            COUNT(f.OrderID) AS Total_Orders,
            (COUNT(CASE WHEN f.CustomerFeedback IN ('Bad', 'Very Bad') THEN 1 END) * 100.0 / NULLIF(COUNT(f.OrderID), 0)) AS Negative_Rate
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_customer c ON f.CustomerID = c.CustomerID
        GROUP BY c.City
        HAVING COUNT(f.OrderID) > 5
        ORDER BY Negative_Rate DESC
        LIMIT 10;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_customer_preferences():
    query = """
        SELECT 
            c.job_group,
            p.car_type,
            p.CarModel,
            COUNT(f.OrderID) AS Total_Orders,
            SUM(CAST(f.Sales AS DOUBLE)) AS Total_Revenue
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_customer c ON f.CustomerID = c.CustomerID
        JOIN scm_db.main.dim_product p ON f.ProductID = p.ProductID
        GROUP BY c.job_group, p.car_type, p.CarModel
        ORDER BY c.job_group, Total_Orders DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_customer_location_focus(job_group, car_model):
    query = f"""
        SELECT 
            c.City,
            c.State,
            COUNT(f.OrderID) AS Total_Orders,
            SUM(CAST(f.Sales AS DOUBLE)) AS Total_Revenue,
            AVG(CAST(f.Sales AS DOUBLE)) AS Avg_Order_Value
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_customer c ON f.CustomerID = c.CustomerID
        JOIN scm_db.main.dim_product p ON f.ProductID = p.ProductID
        WHERE c.job_group = '{job_group}' 
          AND p.CarModel = '{car_model}'
        GROUP BY c.City, c.State
        ORDER BY Total_Orders DESC
        LIMIT 10;
    """
    return con.execute(query).df()

# ==========================================
# PAGE 3 QUERIES (Shipping & Delivery)
# ==========================================

@st.cache_data(ttl=600)
def get_shipping_lead_time(ship_modes):
    if not ship_modes: return pd.DataFrame()
    modes_str = ", ".join([f"'{m}'" for m in ship_modes])
    query = f"""
        SELECT 
            ShipMode,
            AVG(DATEDIFF('day', OrderDateKey, ShipDateKey)) AS Avg_Shipping_Days,
            MAX(DATEDIFF('day', OrderDateKey, ShipDateKey)) AS Max_Shipping_Days
        FROM scm_db.main.fact_sales
        WHERE ShipDateKey IS NOT NULL 
          AND OrderDateKey IS NOT NULL
          AND UPPER(ShipMode) IN ({modes_str})
        GROUP BY ShipMode
        ORDER BY Avg_Shipping_Days;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_shipping_cost_analysis(ship_modes):
    if not ship_modes: return pd.DataFrame()
    modes_str = ", ".join([f"'{m}'" for m in ship_modes])
    query = f"""
        SELECT 
            ShipMode,
            SUM(CAST(Shipping AS DOUBLE)) AS Total_Shipping_Cost,
            SUM(CAST(Sales AS DOUBLE)) AS Total_Sales,
            (SUM(CAST(Shipping AS DOUBLE)) / NULLIF(SUM(CAST(Sales AS DOUBLE)), 0)) * 100 AS Shipping_Revenue_Ratio
        FROM scm_db.main.fact_sales
        WHERE UPPER(ShipMode) IN ({modes_str})
        GROUP BY ShipMode
        ORDER BY Total_Shipping_Cost DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_regional_shipping_performance(ship_modes):
    if not ship_modes: return pd.DataFrame()
    modes_str = ", ".join([f"'{m}'" for m in ship_modes])
    query = f"""
        SELECT 
            c.City,
            c.State,
            f.ShipMode,
            AVG(DATEDIFF('day', f.OrderDateKey, f.ShipDateKey)) AS Avg_Lead_Time,
            SUM(CAST(f.Shipping AS DOUBLE)) AS Total_Shipping_Cost,
            COUNT(f.OrderID) AS Total_Orders
        FROM scm_db.main.fact_sales f
        JOIN scm_db.main.dim_customer c ON f.CustomerID = c.CustomerID
        WHERE UPPER(f.ShipMode) IN ({modes_str})
        GROUP BY c.City, c.State, f.ShipMode
        HAVING COUNT(f.OrderID) > 5
        ORDER BY Avg_Lead_Time DESC;
    """
    return con.execute(query).df()

@st.cache_data(ttl=600)
def get_shipping_vs_feedback(ship_modes):
    if not ship_modes: return pd.DataFrame()
    modes_str = ", ".join([f"'{m}'" for m in ship_modes])
    query = f"""
        SELECT 
            CustomerFeedback,
            AVG(DATEDIFF('day', OrderDateKey, ShipDateKey)) AS Avg_Lead_Time,
            AVG(CAST(Shipping AS DOUBLE)) AS Avg_Shipping_Fee
        FROM scm_db.main.fact_sales
        WHERE CustomerFeedback IS NOT NULL
          AND UPPER(ShipMode) IN ({modes_str})
        GROUP BY CustomerFeedback
        ORDER BY 
            CASE CustomerFeedback
                WHEN 'Very Bad' THEN 1
                WHEN 'Bad' THEN 2
                WHEN 'Okay' THEN 3
                WHEN 'Good' THEN 4
                WHEN 'Very Good' THEN 5
            END;
    """
    return con.execute(query).df()

# ==========================================
# DASHBOARD UI
# ==========================================

st.title("Car SCM Data Dashboard")
st.markdown("---")

# Navigation Sidebar
st.sidebar.header("Navigation Menu")
page = st.sidebar.radio(
    "Navigate to:",
    ["Sales Overview", "Customer Feedback"]
)

# ----------------------------------------------------------------------
# PAGE 1: SALES OVERVIEW
# ----------------------------------------------------------------------
if page == "1. Sales Overview":
    st.header("Sales & Revenue Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        highest_car_df = get_highest_sales_car()
        if not highest_car_df.empty:
            maker = highest_car_df['CarMaker'].iloc[0]
            model = highest_car_df['CarModel'].iloc[0]
            qty = highest_car_df['Total_Quantity_Sold'].iloc[0]
            st.metric("Best Selling Car", f"{maker} {model}", f"{qty:,.0f} units")
            
    with col2:
        avg_sales_df = average_sales()
        if not avg_sales_df.empty:
            avg_val = avg_sales_df['Average_Order_Value'].iloc[0]
            if pd.notnull(avg_val):
                st.metric("Average Order Value", f"${avg_val:,.2f}")
            else:
                st.metric("Average Order Value", "$0.00")
            
    with col3:
        supplier_df = get_revenue_by_supplier()
        if not supplier_df.empty:
            total_rev = supplier_df['Total_Revenue'].sum()
            st.metric("Total System Revenue", f"${total_rev:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Revenue per Month")
        df_rev_month = revenue_per_month()
        if not df_rev_month.empty:
            df_rev_month['Date'] = pd.to_datetime(df_rev_month['Year'].astype(str) + '-' + df_rev_month['Month'].astype(str) + '-01')
            df_rev_month = df_rev_month.sort_values('Date')
            fig_month = px.line(df_rev_month, x='Date', y='Monthly_Revenue', markers=True, labels={'Monthly_Revenue': 'Revenue ($)', 'Date': 'Time'})
            st.plotly_chart(fig_month, use_container_width=True)

    with col_chart2:
        st.subheader("Average Revenue by Car Type")
        df_sales_car = sales_per_car()
        if not df_sales_car.empty:
            fig_type = px.bar(df_sales_car, x='car_type', y='Average_Revenue_Per_Transaction', color='car_type', text_auto='.2s')
            st.plotly_chart(fig_type, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        st.subheader("Top 10 Car Models by Revenue")
        df_rev_model = revenue_per_carmodel().head(10)
        if not df_rev_model.empty:
            fig_model = px.bar(df_rev_model, x='Total_Revenue', y='CarModel', orientation='h', text_auto='.2s').update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_model, use_container_width=True)
            
    with col_chart4:
        st.subheader("Revenue Distribution by Credit Card Type")
        df_credit = revenue_per_credit()
        if not df_credit.empty:
            fig_credit = px.pie(df_credit, values='Total_Revenue', names='CreditCardType', hole=0.3)
            st.plotly_chart(fig_credit, use_container_width=True)

# ----------------------------------------------------------------------
# PAGE 2: CUSTOMER FEEDBACK
# ----------------------------------------------------------------------
elif page == "2. Customer Feedback":
    st.header("Customer Feedback Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Feedback Ratio")
        df_feedback = get_feedback_distribution()
        if not df_feedback.empty:
            fig_fb = px.pie(df_feedback, values='Total_Feedbacks', names='CustomerFeedback')
            st.plotly_chart(fig_fb, use_container_width=True)
            
    with col2:
        st.subheader("Revenue by Feedback Level")
        df_rev_feedback = get_revenue_by_feedback()
        if not df_rev_feedback.empty:
            fig_rev_fb = px.bar(df_rev_feedback, x='CustomerFeedback', y='Total_Revenue', color='CustomerFeedback', text_auto='.2s')
            st.plotly_chart(fig_rev_fb, use_container_width=True)
            
    st.markdown("---")
    
    st.subheader("Top 10 Cities with Highest Negative Feedback Rate (Bad / Very Bad)")
    df_neg_city = get_negative_feedback_by_city()
    if not df_neg_city.empty:
        fig_neg = px.bar(df_neg_city, x='City', y='Negative_Rate', text_auto='.2f', labels={'Negative_Rate': 'Negative Rate (%)'})
        st.plotly_chart(fig_neg, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Customer Preference Lookup (Interactive)")
    df_prefs = get_customer_preferences()
    
    if not df_prefs.empty:
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            job_groups = df_prefs['job_group'].dropna().unique()
            selected_job = st.selectbox("Select Job Group:", sorted(job_groups))
        with col_sel2:
            car_models = df_prefs[df_prefs['job_group'] == selected_job]['CarModel'].dropna().unique()
            selected_model = st.selectbox("Select Car Model:", sorted(car_models))
            
        if st.button("View Concentration Area", type="primary"):
            df_focus = get_customer_location_focus(selected_job, selected_model)
            if not df_focus.empty:
                st.dataframe(df_focus, use_container_width=True, hide_index=True)
            else:
                st.info("No order data for this job group and car model combination.")
