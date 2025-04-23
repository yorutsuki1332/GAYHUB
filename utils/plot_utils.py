import plotly.graph_objects as go
from collections import Counter, defaultdict
from dash import Dash, html, dcc, Input, Output
import pandas as pd
from datetime import datetime
import webbrowser
import os
from model.word_cloud_analyzer import WordCloudAnalyzer

def plot_sentiment_distribution_with_percentages(sentiments):
    # Define all possible sentiments
    all_sentiments = ['positive', 'neutral', 'negative']
    
    # Count the number of each sentiment
    sentiment_counts = Counter(sentiments)
    
    # Ensure all sentiments are present
    for sentiment in all_sentiments:
        if sentiment not in sentiment_counts:
            sentiment_counts[sentiment] = 0
    
    # Sort the counts by our defined order
    sentiment_counts = {k: sentiment_counts[k] for k in all_sentiments}
    
    total = sum(sentiment_counts.values())
    
    # Calculate percentages
    percentages = {sentiment: (count / total) * 100 if total > 0 else 0 
                  for sentiment, count in sentiment_counts.items()}

    # Create color mapping
    colors = {'positive': '#2ecc71', 'neutral': '#3498db', 'negative': '#e74c3c'}

    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(sentiment_counts.keys()),
            y=list(sentiment_counts.values()),
            text=[f"{percentages[s]:.1f}%" for s in sentiment_counts.keys()],
            textposition='outside',
            marker_color=[colors[s] for s in sentiment_counts.keys()]
        )
    ])

    # Update layout
    fig.update_layout(
        title="Sentiment Distribution with Percentages",
        xaxis_title="Sentiment",
        yaxis_title="Number of Reviews",
        template="plotly_white",
        showlegend=False
    )

    fig.show()

def plot_topic_sentiment_distribution(reviews_with_topics):
    # Organize data by topic and sentiment
    topic_sentiment_counts = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
    for review in reviews_with_topics:
        for topic in review['topics']:
            topic_sentiment_counts[topic][review['sentiment']] += 1

    topics = list(topic_sentiment_counts.keys())
    
    # Create traces for each sentiment
    fig = go.Figure(data=[
        go.Bar(
            name='Positive',
            x=topics,
            y=[topic_sentiment_counts[topic]['positive'] for topic in topics],
            marker_color='#2ecc71'
        ),
        go.Bar(
            name='Neutral',
            x=topics,
            y=[topic_sentiment_counts[topic]['neutral'] for topic in topics],
            marker_color='#3498db'
        ),
        go.Bar(
            name='Negative',
            x=topics,
            y=[topic_sentiment_counts[topic]['negative'] for topic in topics],
            marker_color='#e74c3c'
        )
    ])

    # Update layout
    fig.update_layout(
        barmode='stack',
        title="Sentiment Distribution by Topic",
        xaxis_title="Topics",
        yaxis_title="Number of Reviews",
        template="plotly_white",
        xaxis_tickangle=-45,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )

    fig.show()

def create_dashboard(reviews_with_topics):
    app = Dash(__name__)
    
    # Convert dates to datetime
    df = pd.DataFrame(reviews_with_topics)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get date range for slider
    date_range = pd.date_range(
        start=df['date'].min(),
        end=df['date'].max(),
        freq='ME'  # Changed from 'M' to 'ME'
    )

    app.layout = html.Div([
        html.H1('Restaurant Reviews Dashboard'),
        
        # Date range selector
        html.Div([
            html.Label('Select Date Range:'),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=df['date'].min(),
                max_date_allowed=df['date'].max(),
                start_date=df['date'].min(),
                end_date=df['date'].max()
            ),
        ]),

        # Graphs
        html.Div([
            dcc.Graph(id='sentiment-distribution'),
            dcc.Graph(id='topic-distribution')
        ])
    ])

    @app.callback(
        [Output('sentiment-distribution', 'figure'),
         Output('topic-distribution', 'figure')],
        [Input('date-picker', 'start_date'),
         Input('date-picker', 'end_date')]
    )
    def update_graphs(start_date, end_date):
        # Filter data based on selected date range
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df[mask]

        # Sentiment distribution figure
        all_sentiments = ['positive', 'neutral', 'negative']
        sentiment_counts = Counter(filtered_df['sentiment'])
        
        # Ensure all sentiments are present
        for sentiment in all_sentiments:
            if sentiment not in sentiment_counts:
                sentiment_counts[sentiment] = 0
        
        # Sort the counts by our defined order
        sentiment_counts = {k: sentiment_counts[k] for k in all_sentiments}
        
        total = sum(sentiment_counts.values())
        percentages = {s: (c/total)*100 if total > 0 else 0 for s, c in sentiment_counts.items()}
        
        colors = {'positive': '#2ecc71', 'neutral': '#3498db', 'negative': '#e74c3c'}
        
        sentiment_fig = go.Figure(data=[
            go.Bar(
                x=list(sentiment_counts.keys()),
                y=list(sentiment_counts.values()),
                text=[f"{percentages[s]:.1f}%" for s in sentiment_counts.keys()],
                textposition='outside',
                marker_color=[colors[s] for s in sentiment_counts.keys()]
            )
        ])
        
        sentiment_fig.update_layout(
            title="Sentiment Distribution",
            xaxis_title="Sentiment",
            yaxis_title="Number of Reviews",
            template="plotly_white",
            showlegend=False
        )

        # Topic distribution figure
        topic_sentiment_counts = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
        for _, row in filtered_df.iterrows():
            for topic in row['topics']:
                topic_sentiment_counts[topic][row['sentiment']] += 1

        topics = list(topic_sentiment_counts.keys())
        
        topic_fig = go.Figure(data=[
            go.Bar(
                name='Positive',
                x=topics,
                y=[topic_sentiment_counts[topic]['positive'] for topic in topics],
                marker_color='#2ecc71'
            ),
            go.Bar(
                name='Neutral',
                x=topics,
                y=[topic_sentiment_counts[topic]['neutral'] for topic in topics],
                marker_color='#3498db'
            ),
            go.Bar(
                name='Negative',
                x=topics,
                y=[topic_sentiment_counts[topic]['negative'] for topic in topics],
                marker_color='#e74c3c'
            )
        ])

        topic_fig.update_layout(
            barmode='stack',
            title="Sentiment Distribution by Topic",
            xaxis_title="Topics",
            yaxis_title="Number of Reviews",
            template="plotly_white",
            xaxis_tickangle=-45,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )

        return sentiment_fig, topic_fig

    return app

def create_html_dashboard(reviews_with_topics):
    # Initialize word cloud analyzer
    word_cloud_analyzer = WordCloudAnalyzer()
    word_frequencies = word_cloud_analyzer.get_word_frequencies(reviews_with_topics)
    word_cloud_fig = word_cloud_analyzer.create_word_cloud_plot(word_frequencies)
    
    # Create the HTML file
    html_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Results</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            .plot-container { margin-bottom: 30px; }
            body { padding: 20px; max-width: 1200px; margin: 0 auto; }
            h1 { text-align: center; margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <h1>Restaurant Review Analysis</h1>
        <div id="wordcloud-plot" class="plot-container"></div>
        <div id="sentiment-plot" class="plot-container"></div>
        <div id="topic-plot" class="plot-container"></div>
        <script>
    """
    
    # Generate sentiment distribution data
    all_sentiments = ['positive', 'neutral', 'negative']
    sentiment_counts = Counter([r['sentiment'] for r in reviews_with_topics])
    
    # Ensure all sentiments are present
    for sentiment in all_sentiments:
        if sentiment not in sentiment_counts:
            sentiment_counts[sentiment] = 0
    
    # Sort the counts by our defined order
    sentiment_counts = {k: sentiment_counts[k] for k in all_sentiments}
    
    total = sum(sentiment_counts.values())
    percentages = {s: (c/total)*100 if total > 0 else 0 for s, c in sentiment_counts.items()}
    colors = {'positive': '#2ecc71', 'neutral': '#3498db', 'negative': '#e74c3c'}
    
    sentiment_data = {
        'x': list(sentiment_counts.keys()),
        'y': list(sentiment_counts.values()),
        'text': [f"{percentages[s]:.1f}%" for s in sentiment_counts.keys()],
        'type': 'bar',
        'marker': {'color': [colors[s] for s in sentiment_counts.keys()]}
    }
    
    # Generate topic distribution data
    topic_sentiment_counts = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
    for review in reviews_with_topics:
        for topic in review['topics']:
            topic_sentiment_counts[topic][review['sentiment']] += 1
    
    topics = list(topic_sentiment_counts.keys())
    
    topic_data = [
        {
            'name': 'Positive',
            'x': topics,
            'y': [topic_sentiment_counts[topic]['positive'] for topic in topics],
            'type': 'bar',
            'marker': {'color': '#2ecc71'}
        },
        {
            'name': 'Neutral',
            'x': topics,
            'y': [topic_sentiment_counts[topic]['neutral'] for topic in topics],
            'type': 'bar',
            'marker': {'color': '#3498db'}
        },
        {
            'name': 'Negative',
            'x': topics,
            'y': [topic_sentiment_counts[topic]['negative'] for topic in topics],
            'type': 'bar',
            'marker': {'color': '#e74c3c'}
        }
    ]
    
    # Convert the word cloud figure to JSON and include it in the HTML
    word_cloud_json = word_cloud_fig.to_json()
    
    html_content += f"""
        var wordCloudData = {word_cloud_json};
        var sentimentData = {sentiment_data};
        var topicData = {topic_data};
        
        var wordCloudLayout = {{
            title: 'Most Common Words in Reviews',
            showlegend: false,
            xaxis: {{visible: false}},
            yaxis: {{visible: false}},
            hovermode: 'closest',
            template: 'plotly_white',
            height: 500,
            margin: {{t: 50, b: 20, l: 20, r: 20}}
        }};
        
        var sentimentLayout = {{
            title: 'Sentiment Distribution',
            xaxis: {{title: 'Sentiment'}},
            yaxis: {{title: 'Number of Reviews'}},
            template: 'plotly_white',
            height: 400
        }};
        
        var topicLayout = {{
            title: 'Sentiment Distribution by Topic',
            xaxis: {{title: 'Topics', tickangle: -45}},
            yaxis: {{title: 'Number of Reviews'}},
            barmode: 'stack',
            template: 'plotly_white',
            height: 500
        }};
        
        Plotly.newPlot('wordcloud-plot', wordCloudData.data, wordCloudLayout);
        Plotly.newPlot('sentiment-plot', [sentimentData], sentimentLayout);
        Plotly.newPlot('topic-plot', topicData, topicLayout);
        </script>
    </body>
    </html>
    """
    
    # Save and open the HTML file
    output_path = os.path.join(os.path.dirname(__file__), 'results.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open the file in the default web browser (with proper file:// URL format)
    abs_path = os.path.abspath(output_path)
    url = f'file:///{abs_path.replace(os.sep, "/")}'
    webbrowser.open(url)

def run_dashboard(reviews_with_topics):
    app = create_dashboard(reviews_with_topics)
    app.run(debug=False, host='localhost', port=8050)

def run_analysis(reviews_with_topics):
    create_html_dashboard(reviews_with_topics)