import requests
from bs4 import BeautifulSoup as bs
import streamlit as st
import pandas as pd
import time
import plotly.express as px

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

def scrape_central_charts(pages_count=7):
    strt_time = time.time()

    url_start = 'https://www.centralcharts.com/en/price-list-ranking/'
    url_end = 'ALL/asc/ts_82-cryptocurrencies-usd--qc_1-alphabetical-order?p={}'

    values_list = []

    for page_number, page in enumerate([url_end.format(i) for i in range(1, pages_count + 1)], start=1):
        url = url_start + page

        with requests.get(url) as webpage:
            if webpage.status_code == 200:
                soup = bs(webpage.text, 'html.parser')

                stock_table = soup.find('table', class_='tabMini tabQuotes')

                if stock_table:
                    tr_tag_list = stock_table.find_all('tr')

                    for each_tr_tag in tr_tag_list[1:]:
                        td_tag_list = each_tr_tag.find_all('td')

                        row_values = [each_td_tag.text.strip() for each_td_tag in td_tag_list[:7]]
                        values_list.append(row_values)

    return values_list

@st.cache_data
def get_data():
    # get the data from the website
    data = scrape_central_charts()
    df = pd.DataFrame(data, columns=['Name', 'Price', 'Change', 'Low', 'High', 'Open', 'Volume'])
    # Convert 'Price' column to numeric
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    
    return df

# Create a function to generate the pie chart
def create_pie_chart(df):
    total_volume = df['Volume'].sum()
    volume_pie_chart = px.pie(df, values='Volume', names='Name', title=f'Total Volume Occupations (Total Volume: {total_volume})')
    return volume_pie_chart

# Call the Streamlit app logic
def start_app():
    # Retrieve the data using st.cache
    df = get_data()

    st.header('Crypto Prices')
    
    # Display the current time
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    st.write(f'Data last fetched at: {current_time}')

    
    # Display an image
    st.image('crypto.png', use_column_width=True)

    
    # Display the data using Streamlit
    st.dataframe(df)

    # Allow users to filter by cryptocurrency name
    selected_crypto = st.selectbox('Select Cryptocurrency:', df['Name'].unique())

    # Filter the DataFrame based on the selected cryptocurrency
    selected_data = df[df['Name'] == selected_crypto]

    # Display the filtered data
    st.dataframe(selected_data)

    # Create a bar chart for the top 10 priced cryptocurrencies
    top_10_chart = px.bar(df.nlargest(10, 'Price'), x='Name', y='Price', title='Top 10 Priced Cryptocurrencies')
    st.plotly_chart(top_10_chart)


if __name__ == '__main__':
    # Call the Streamlit app logic
    start_app()
    print(time.time())