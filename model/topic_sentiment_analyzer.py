from transformers import pipeline

class TopicSentimentAnalyzer:
    def __init__(self):
        # Load both sentiment and topic analysis pipelines
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis", 
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
        self.topic_model = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli"
        )

    def get_sentiment(self, text, rating=None):
        """Analyze sentiment of given text with optional rating consideration"""
        sentiment_result = self.sentiment_analyzer(text)[0]
        score = int(sentiment_result['label'].split()[0])
        
        # If rating is provided, use it to adjust the sentiment
        if rating is not None:
            if rating >= 4:
                sentiment = "positive"
            elif rating <= 2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        else:
            # Use the model's prediction if no rating
            if score >= 4:
                sentiment = "positive"
            elif score <= 2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
        return {
            "sentiment": sentiment,
            "confidence": sentiment_result['score']
        }

    def get_topics(self, text, threshold=0.2):
        """Analyze topics in given text"""
        candidate_labels = [
            "food quality", "service", "ambiance", 
            "price", "cleanliness", "wait time", 
            "menu variety", "portion size"
        ]
        topic_result = self.topic_model(text, candidate_labels)
        
        topics = [
            label for label, score 
            in zip(topic_result['labels'], topic_result['scores']) 
            if score > threshold
        ]
        
        return topics if topics else ["general feedback"]

    def analyze_comment(self, comment, rating=None):
        """Complete analysis of a comment including sentiment and topics"""
        # Get topics
        topics = self.get_topics(comment)
        
        # Get sentiment with rating consideration
        sentiment_results = self.get_sentiment(comment, rating)
        
        return {
            "comment": comment,
            "topics": topics,
            **sentiment_results
        }