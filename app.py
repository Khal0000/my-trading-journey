from os import write
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(
    page_title="My Charting Tools",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header
st.markdown("<h1 style='text-align: center; color:  #34eb95; font-size: 42px ;'>Charts at a Glance</h1>", unsafe_allow_html=True)
st.markdown("""<hr style="height:10x;border:none;color:#34eb95;background-color:#333;" /> """, unsafe_allow_html=True)

# Program
col1,col2,col3 = st.columns(3)
with col1:
    selected_stock = st.text_input("Enter a valid ticker...", "^JKSE")
with col2:
    periods = st.selectbox(label = 'Select the periods :', options=('1d','5d','1mo','3mo','6mo','1y','5y','ytd','max'), index=7)
with col3:
    legend=st.selectbox(label = 'Show legend', options=(True,False), index=1)

# Chart
get_data = yf.Ticker(selected_stock)
df = pd.DataFrame(get_data.history(period=periods), columns=['Open','High', 'Low', 'Close', 'Volume'])
df['MA20'] = df['Close'].rolling(window=20, min_periods=0).mean()
df['MA50'] = df['Close'].rolling(window=50, min_periods=0).mean()
df['MA200'] = df['Close'].rolling(window=200, min_periods=0).mean()
df['diff'] = df['Close'] - df['Open']
df.loc[df['diff']>=0, 'color'] = 'lightseagreen'
df.loc[df['diff']<0, 'color'] = 'tomato'
df['volbtc_MA_20'] = df['Volume'].rolling(20).mean()

# MACD : 12 day EMA - 26-day ema
df['26_ema'] = df['Close'].ewm(span=26,min_periods=0,adjust=True,ignore_na=False).mean()
df['12_ema'] = df['Close'].ewm(span=12,min_periods=0,adjust=True,ignore_na=False).mean()
df['MACD'] = df['12_ema'] - df['26_ema']
df['signal'] = df['MACD'].ewm(span=9,min_periods=0,adjust=True,ignore_na=False).mean()


fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=(f'{selected_stock}', '', 'MACD'), row_width=[0.3,0.2,1])

fig.add_trace(go.Candlestick(x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'], name = 'Price',increasing_line_color= 'lightseagreen', decreasing_line_color= 'tomato'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], marker_color='green', name='MA20', opacity=0.5), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], marker_color='yellow', name='MA50', opacity=0.5), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], marker_color='red', name='MA200', opacity=0.5), row=1, col=1)
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], showlegend=False, marker={'color':df['color']}), row=2, col=1)
vol_btc = go.Scatter(x=df.index, y=df['volbtc_MA_20'], mode='lines', name='ma 20', showlegend=False)
fig.add_trace(vol_btc, row=2, col=1)


# plot MACD
fig.add_trace(go.Scatter(x=df.index,
                            y=df['MACD'], name='MACD', showlegend=False), row=3, col=1) 
fig.add_trace(go.Scatter(x=df.index,
                            y=df['signal'], name = 'Signal', showlegend=False), row=3, col=1) 

fig.update_layout(
        xaxis_tickfont_size = 12,
        yaxis = dict(
            title = 'Price',
            titlefont_size=14,
            tickfont_size=12
        ),
        autosize=False,
        width=800,
        height=800,
        # margin=dict(l=50, r=50, b=100, t=100, pad=5),
        paper_bgcolor = 'Black'
    )

# Plot RSI
# Plot Stochastic


fig.update(layout_xaxis_rangeslider_visible=False)
fig.update_layout(template='plotly_dark')
fig.update_layout(dragmode='pan')
fig.update_layout(showlegend=legend)
st.plotly_chart(fig, use_container_width=True)
