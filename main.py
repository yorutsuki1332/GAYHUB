from flask import Flask, render_template, jsonify, request
import src.main as analyze_reviews
import threading
import json
from api.scrap_reviews import scrape_full_reviews_to_json
from model.word_cloud_analyzer import WordCloudAnalyzer

app = Flask(__name__)
analysis_status = {"running": False, "completed": False, "error": None}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_reviews():
    # Log the request method to debug
    app.logger.info(f"Received request with method: {request.method}")
    
    url = request.form.get('restaurant_url')
    if not url:
        return "Error: No URL provided", 400

    try:
        # Scrape reviews and save to JSON
        scrape_full_reviews_to_json(url=url, max_pages=5)
        return render_template('results.html')
    except Exception as e:
        app.logger.error(f"Error during scraping: {str(e)}")
        return f"Error occurred during scraping: {str(e)}", 500


@app.route('/word_cloud')
def word_cloud():
    try:
        # Read reviews from JSON file
        with open('data/reviews.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format reviews
        reviews_formatted = [{"review": r["text"], "date": r["date"]} for r in data]
        
        # Create word cloud
        analyzer = WordCloudAnalyzer()
        frequencies = analyzer.get_word_frequencies(reviews_formatted)
        fig = analyzer.create_word_cloud_plot(frequencies)
        
        # Convert to div format for direct embedding
        plot_div = fig.to_html(full_html=False, include_plotlyjs=False)
        return plot_div
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start_analysis')
def start_analysis():
    if not analysis_status["running"]:
        analysis_status["running"] = True
        analysis_status["completed"] = False
        analysis_status["error"] = None
        
        def run_analysis():
            try:
                analyze_reviews()
                analysis_status["completed"] = True
            except Exception as e:
                analysis_status["error"] = str(e)
            finally:
                analysis_status["running"] = False
        
        thread = threading.Thread(target=run_analysis)
        thread.start()
    
    return jsonify(analysis_status)

@app.route('/status')
def get_status():
    return jsonify(analysis_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
