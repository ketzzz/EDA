import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf

st.title('S&P 500 Tracker')

st.markdown("""
This app performs simple webscraping of S&P 500 data!
* **Python libraries:** base64, pandas, streamlit, matplotlib, yfinance
* **Datasource:** [Wikipedia.org](https://en.wikipedia.org/).
""")

st.sidebar.header('Filter')

# web scraping of S&P 500 data
@st.cache_data
def load_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header = 0) # read_html only reads tables, not paragraphs
    df = html[0]
    return df

df = load_data()

# Sidebar - Sector
sorted_sector = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector, sorted_sector)

# Sidebar - Number of companies
num_companies = st.sidebar.slider('No. of companies', 1, 5)

# Filtering data
df_selected = df[(df['GICS Sector'].isin(selected_sector))]
st.header('Data of S&P 500 companies in selected sectors')
st.write('Data Dimension: ' + str(df_selected.shape[0]) + ' rows and ' + str(df_selected.shape[1]) + ' columns.')
st.dataframe(df_selected)

# download S&P 500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode() # strings <-> bytes conversion
    href = f'<a href="data:file/csv;base64,{b64}" download="s&p500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected), unsafe_allow_html=True)

data = yf.download(
    tickers = list(df_selected[:6].Symbol),
    period = "ytd",
    interval = "1d",
    group_by= "ticker",
    auto_adjust=True,
    prepost=True,
    threads=True,
    proxy=None
)

def price_plot(symbol):
    df=pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    fig, ax = plt.subplots(figsize=(7, 5))
    plt.fill_between(df.Date, df.Close, color='pink',alpha=0.3)
    plt.plot(df.Date, df.Close, color='pink',alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Closing Price', fontweight='bold')
    return st.pyplot(fig)

st.header('Stock Closing Price')
for i in list(df_selected.Symbol)[:num_companies]:
    price_plot(i)

