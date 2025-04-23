import os
import sys
import json

# Ensure the parent directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.topic_sentiment_analyzer import TopicSentimentAnalyzer
from utils.plot_utils import run_analysis

# Ensure UTF-8 encoding for console output
sys.stdout.reconfigure(encoding='utf-8')

def main():
    # Path to the JSON file containing reviews
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'reviews.json')

    # Initialize the analyzer
    topic_sentiment_analyzer = TopicSentimentAnalyzer()

    # Read reviews from the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process only first xx reviews
    data = data[:5]
    
    print(f"Analyzing {len(data)} reviews...\n")
    
    # Analyze each review
    reviews_with_topics = []
    for review_data in data:
        if 'text' in review_data and 'date' in review_data:  # Make sure review has required fields
            # Pass both text and rating to the analyzer
            rating = review_data.get('rating')
            analysis_result = topic_sentiment_analyzer.analyze_comment(review_data['text'], rating)
            
            reviews_with_topics.append({
                "review": review_data['text'],
                "date": review_data['date'],
                "topics": analysis_result['topics'],
                "sentiment": analysis_result['sentiment'],
                "rating": rating
            })

            print(f"Review: {review_data['text'][:100]}...")  # Print first 100 chars only
            print(f"Date: {review_data['date']}")
            if rating is not None:
                print(f"Rating: {rating}")
            print(f"Sentiment: {analysis_result['sentiment']}")
            print(f"Topics: {', '.join(analysis_result['topics']) if analysis_result['topics'] else 'None'}")
            print("-" * 80 + "\n")

    # Run analysis
    run_analysis(reviews_with_topics)

if __name__ == "__main__":
    main()