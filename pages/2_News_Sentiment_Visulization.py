import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock News Sentiment", layout="wide")

# Sidebar for user input
st.sidebar.header("Settings")
tickers = st.sidebar.text_input("Enter ticker symbols (comma-separated)", "AAPL")
api_key = st.sidebar.text_input("Enter your Alpha Vantage API key", type="password")

if st.sidebar.button("Fetch Data"):
    if not api_key:
        st.error("Please enter your Alpha Vantage API key.")
    else:
        # Fetch data from Alpha Vantage API
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers}&apikey={api_key}'
        r = requests.get(url)
        data = r.json()

        if "Error Message" in data:
            st.error("API Error: " + data["Error Message"])
        elif "feed" not in data:
            st.error("No data available. Please check your API key and ticker symbols.")
        else:
            # Process and display data
            st.title("Stock News Sentiment Analysis")

            # Prepare data for visualization
            df = pd.DataFrame(data['feed'])
            df['time_published'] = pd.to_datetime(df['time_published'], format='%Y%m%dT%H%M%S')
            df['date'] = df['time_published'].dt.date

            # Calculate sentiment scores
            df['sentiment_score'] = df['overall_sentiment_score'].astype(float)
            df['sentiment_label'] = pd.cut(df['sentiment_score'], 
                                           bins=[-float('inf'), -0.35, -0.15, 0.15, 0.35, float('inf')],
                                           labels=['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'])

            # Create sentiment trend chart
            fig = go.Figure()

            for label in df['sentiment_label'].unique():
                mask = df['sentiment_label'] == label
                fig.add_trace(go.Scatter(x=df.loc[mask, 'time_published'], 
                                         y=df.loc[mask, 'sentiment_score'],
                                         mode='markers',
                                         name=label,
                                         text=df.loc[mask, 'title']))

            fig.update_layout(title='Sentiment Trend',
                              xaxis_title='Date',
                              yaxis_title='Sentiment Score',
                              height=600)

            st.plotly_chart(fig, use_container_width=True)

            # Display recent news
            st.header("Recent News")
            for _, article in df.sort_values('time_published', ascending=False).head(10).iterrows():
                st.subheader(article['title'])
                st.write(f"Published: {article['time_published']}")
                st.write(f"Sentiment: {article['sentiment_label']}")
                st.write(article['summary'])
                st.write("---")

else:
    st.info("Enter your API key and ticker symbols in the sidebar, then click 'Fetch Data' to begin.")
