import re
from collections import Counter
import plotly.graph_objects as go
import numpy as np
import math
import random

class WordCloudAnalyzer:
    def __init__(self):
        # Define stop words directly (most common English stop words + custom words for restaurant reviews)
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
            "so", "always", "can't", "couldn't", "didn't", "doesn't", "hadn't", "hasn't",
            "there", "here", "where", "when", "why", "how", "what's", "who's", "who've",
            "who'd", "won't", "wouldn't", "isn't", "ain't", "aren't", "wasn't", "weren't",
            "hasn't", "haven't", "shouldn't", "couldn't", "mightn't", "mustn't", "needn't",
            "shan't", "won't", "wouldn't", "you'd", "you'll", "you're", "you've",
            "never", "ever", "always", "sometimes", "often", "seldom",
            "every", "each", "any", "some", "all", "most", "few", "less", "more",
            "much", "many", "both", "either", "neither", "one", "two", "three",
            "four", "five", "six", "seven", "eight", "nine", "ten", "first", "second",
            "third", "last", "next", "last", "then", "now", "later", "before",
            "after", "during", "while", "until", "since", "for", "with", "about",
            "against", "between", "into", "through", "across", "along", "around",
            "over", "under", "above", "below", "near", "far", "close", "away", "no", "not", "will",
            "shall", "should", "can", "could", "may", "might", "must", "ought", "wait", 
            "up", "down", "left", "right", "in", "out", "on", "off", "at", "re",
            "to", "from", "by", "for", "of", "about", "as", "like", "such", "than",
            "than", "with", "without", "within", "besides", "except", "but", "or",
            "you'd", "you'll", "you're", "you've", "you'd", "you'll", "you're", "you've",
            "haven't", "isn't", "mightn't", "mustn't", "needn't", "shan't", "shouldn't",
            "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself',
            'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
            'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by',
            'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
            'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
            'restaurant', 'food', 'place', 'would', 'really', 'got', 'get', 'also',
            'bit', 'one', 'two', 'three', 'four', 'five', 'time','just', 'very', 'much', 'more', 'less'
        }

    def preprocess_text(self, text):
        # Convert to lowercase
        text = text.lower()
        
        # Split text into words using regex (splits on whitespace and punctuation)
        words = re.findall(r'\b\w+\b', text)
        
        # Remove stop words and single characters
        words = [word for word in words if word not in self.stop_words and len(word) > 1]
        
        return words

    def get_word_frequencies(self, reviews):
        all_words = []
        for review in reviews:
            words = self.preprocess_text(review['review'])
            all_words.extend(words)
        
        # Get word frequencies
        word_freq = Counter(all_words)
        return dict(word_freq.most_common(30))  # Return top 30 words

    def create_word_cloud_plot(self, word_frequencies):
        words = list(word_frequencies.keys())
        freqs = list(word_frequencies.values())
        max_freq = max(freqs)
        
        # Calculate sizes (between 5 and 50)
        sizes = [3 + (freq / max_freq) * 50 for freq in freqs]
        
        # Sort words by frequency (highest to lowest)
        sorted_items = sorted(zip(words, freqs, sizes), key=lambda x: x[1], reverse=True)
        words, freqs, sizes = zip(*sorted_items)
        
        # Calculate positions in a spiral pattern
        positions = []
        texts = []
        x_coords = []
        y_coords = []
        
        # Place most frequent word in center
        center_x, center_y = 0.5, 0.5
        x_coords.append(center_x)
        y_coords.append(center_y)
        texts.append(words[0])
        positions.append((center_x, center_y))
        
        # Place remaining words in a spiral pattern
        angle = 0
        radius_step = 0.05
        for i, (word, size) in enumerate(zip(words[1:], sizes[1:]), 1):
            # Increase angle based on golden ratio for better distribution
            angle += math.pi * (3 - math.sqrt(5))
            # Increase radius as we go outward
            radius = radius_step * math.sqrt(i)
            
            # Calculate position
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Keep position within bounds
            x = max(0.1, min(0.9, x))
            y = max(0.1, min(0.9, y))
            
            x_coords.append(x)
            y_coords.append(y)
            texts.append(word)
            positions.append((x, y))
        
        # Create scatter trace for each word
        traces = []
        for i, ((x, y), word, size, freq) in enumerate(zip(positions, texts, sizes, freqs)):
            # Generate random HSL color
            hue = random.randint(0, 360)  # Random hue between 0-360
            saturation = random.randint(60, 100)  # Random saturation between 60-100%
            lightness = random.randint(40, 60)  # Random lightness between 40-60%
            
            traces.append(
                go.Scatter(
                    x=[x],
                    y=[y],
                    mode='text',
                    text=[word],
                    textfont=dict(
                        size=size,
                        color=f'hsl({hue}, {saturation}%, {lightness}%)'
                    ),
                    hoverinfo='text',
                    hovertext=f'{word}: {freq} occurrences',
                    showlegend=False
                )
            )
        
        # Create figure
        fig = go.Figure(data=traces)
        
        # Update layout
        fig.update_layout(
            title="Word Cloud of Review Terms",
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0, 1]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0, 1]
            ),
            width=800,
            height=600,
            plot_bgcolor='white',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig