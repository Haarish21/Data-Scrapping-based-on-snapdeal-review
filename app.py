from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from textblob import TextBlob
import requests
import matplotlib.pyplot as plt
from wordcloud import WordCloud  # ✅ NEW
import os
import uuid

app = Flask(__name__)

def scrape_reviews(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    review_blocks = soup.find_all('div', class_='user-review')  # Adjust as needed

    reviews = []
    seen = set()

    for block in review_blocks:
        review_text = block.get_text(separator=' ', strip=True)
        if len(review_text) > 30 and review_text not in seen:
            reviews.append(review_text)
            seen.add(review_text)

    return reviews

@app.route('/', methods=['GET', 'POST'])
def index():
    reviews = []
    positive = 0
    negative = 0
    url = ''
    chart_path = None
    wordcloud_path = None  # ✅ NEW

    if request.method == 'POST':
        url = request.form['url']
        reviews = scrape_reviews(url)

        sentiments = []
        all_text = ""
        for r in reviews:
            analysis = TextBlob(r)
            all_text += " " + r
            if analysis.sentiment.polarity > 0:
                sentiments.append(("Positive", r))
                positive += 1
            else:
                sentiments.append(("Negative", r))
                negative += 1

        # ... previous code ...

        if positive + negative > 0:
            # ✅ Bar Graph Generation (instead of pie chart)
            labels = ['Positive', 'Negative']
            values = [positive, negative]
            colors = ['#2ecc71', '#e74c3c']

            fig, ax = plt.subplots()
            bars = ax.bar(labels, values, color=colors)
            ax.set_title('Sentiment Analysis Results')
            ax.set_ylabel('Number of Reviews')
            ax.set_ylim(0, max(values) + 2)  # padding on y-axis
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', va='bottom')

            chart_id = str(uuid.uuid4())
            chart_path = f'static/{chart_id}.png'
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()

            # ✅ Word Cloud Generation remains the same
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
            wordcloud_id = str(uuid.uuid4())
            wordcloud_path = f'static/{wordcloud_id}.png'
            wordcloud.to_file(wordcloud_path)

        return render_template('index.html', reviews=sentiments, url=url, chart=chart_path, wordcloud=wordcloud_path)

    return render_template('index.html', reviews=reviews, url=url, chart=chart_path, wordcloud=wordcloud_path)

if __name__ == '__main__':
    app.run(debug=True)
