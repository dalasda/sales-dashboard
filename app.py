
import streamlit as st
import pandas as pd
import plotly.express as px # Import plotly.express

# Decorate data loading function with cache_data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("sales_data_capstone.csv")
        # Pārveido 'Date' kolonu uz datetime tipu
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        st.error("Kļūda: 'sales_data_capstone.csv' fails nav atrasts. Lūdzu, pārliecinieties, ka fails atrodas tajā pašā direktorijā.")
        return pd.DataFrame() # Return empty DataFrame on error

def main():
    st.set_page_config(page_title="Pārdošanas Panelis", layout="centered")
    st.title("Pārdošanas Panelis")
   
if __name__ == "__main__":
    main()

if st.button("🔄 Pārlādēt datus"):
    st.cache_data.clear()
    st.rerun()

df = load_data()

    # --- Sānjoslas filtri un Datu Pielādēšana ---
    st.sidebar.header("Filtri")

    # Add a reload data button
    if st.sidebar.button("Pārlādēt Datus"): # Moved to sidebar as per common practice for data controls
        st.cache_data.clear()
        st.experimental_rerun()

    # Ielādē CSV failu
    df = load_data()

    if df.empty:
        return # Stop if data loading failed or returned empty


    # Reģiona filtrs
    all_regions = df['Region'].unique()
    selected_regions = st.sidebar.multiselect(
        "Izvēlieties Reģionus",
        options=all_regions,
        default=all_regions
    )

    # Produktu kategorijas filtrs
    all_categories = df['Product_Category'].unique()
    selected_categories = st.sidebar.multiselect(
        "Izvēlieties Produktu Kategorijas",
        options=all_categories,
        default=all_categories
    )

    # Datuma intervāla filtrs
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.sidebar.date_input(
        "Datuma intervāls",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Pielieto filtrus
    filtered_df = df[df['Region'].isin(selected_regions)]
    filtered_df = filtered_df[filtered_df['Product_Category'].isin(selected_categories)]

    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]

    # --- KPI Rādītāji ---
    st.markdown("## Galvenie Veiktspējas Rādītāji")
    col1, col2, col3 = st.columns(3)

    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    average_discount = filtered_df['Discount'].mean() * 100 if not filtered_df.empty else 0

    with col1:
        st.metric(label="Kopējais Apgrozījums", value=f"{total_sales:.2f} €")
    with col2:
        st.metric(label="Kopējā Peļņa", value=f"{total_profit:.2f} €")
    with col3:
        st.metric(label="Vidējā Atlaide", value=f"{average_discount:.2f} %")

    st.subheader("Filtrētie Pārdošanas Dati")
    st.dataframe(filtered_df)

    # --- Diagrammas ar Plotly ---

    if not filtered_df.empty:
        # 1. Line chart: Sales over time (Date vs Sales)
        st.subheader("Pārdošana Laika Gaitā")
        sales_over_time = filtered_df.groupby('Date')['Sales'].sum().reset_index()
        fig_line = px.line(sales_over_time, x='Date', y='Sales', title='Pārdošana laika gaitā')
        st.plotly_chart(fig_line, use_container_width=True)

        # 2. Scatter plot: Sales vs Profit
        st.subheader("Pārdošana pret Peļņu")
        fig_scatter = px.scatter(filtered_df, x='Sales', y='Profit', color='Product_Category',
                                 title='Pārdošana pret peļņu', hover_data=['Product', 'Region'])
        st.plotly_chart(fig_scatter, use_container_width=True)

        # 3. Bar chart: Sales by Product_Category
        st.subheader("Pārdošana pa Produktu Kategorijām")
        sales_by_category = filtered_df.groupby('Product_Category')['Sales'].sum().reset_index()
        fig_bar = px.bar(sales_by_category, x='Product_Category', y='Sales', title='Pārdošana pa produktu kategorijām')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("Nav datu, kas atbilstu izvēlētajiem filtriem.")


if __name__ == "__main__":
    main()
