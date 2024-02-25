from flask import Flask, request, send_file, render_template
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud

app = Flask(__name__)

# Google News API alt, basically gives top 3 articles related to the keyword
def getNews(keyword):
    news = requests.get("https://newsapi.org/v2/everything?q="+keyword+"&apiKey=64b9e92edc7e43b89c7944864d55d299")
    newsList = news.json().get('articles', [])
    return newsList[:3]

# Gets words that are related to the keyword by scraping from Google, use this for word cloud
def getWords(keyword):
    html = requests.get("https://www.google.com/search?q="+ keyword).content
    soup = BeautifulSoup(html, 'html.parser')
    wordList = []
    for i in soup.find_all():
        wordList.append(i.get_text())
    return wordList

# Makes a word cloud
def wordCloud(keyword):
    wordList = nltk.word_tokenize(keyword)
    goodWords = [word for word in wordList if word not in stopwords.words('english')]
    freq = nltk.FreqDist(goodWords)
    wordcloud = WordCloud(
        width=800,
        height=400,
        random_state=21,
        max_font_size=110,
        background_color=None,
        mode='RGBA'
    ).generate_from_frequencies(freq)
    wordcloud.to_file('static/wordcloud.png')
    return 'static/wordcloud.png'

@app.route('/')
def index():
    return render_template('index.html')

#Lightcast skills API, basically a summary of the keyword
def summarize(keyword):
    headers = {
        'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjNDNjZCRjIzMjBGNkY4RDQ2QzJERDhCMjI0MEVGMTFENTZEQkY3MUYiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJQR2FfSXlEMi1OUnNMZGl5SkE3eEhWYmI5eDgifQ.eyJuYmYiOjE3MDg4ODQ3NTMsImV4cCI6MTcwODg4ODM1MywiaXNzIjoiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20iLCJhdWQiOlsiZW1zaV9vcGVuIiwiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20vcmVzb3VyY2VzIl0sImNsaWVudF9pZCI6Im1zYXozMjFsd25sNmV0c2IiLCJlbWFpbCI6Im5ld21hamlhaWRAZ21haWwuY29tIiwiY29tcGFueSI6ImUiLCJuYW1lIjoiRSIsImlhdCI6MTcwODg4NDc1Mywic2NvcGUiOlsiZW1zaV9vcGVuIl19.nqzzkch_TnfLCH48Pw5yEM_xa8zZMPX9KlGVkBhZGRpUWOZOff3_cwU-jkrNcPo8P7UGToHZITB_zm22KpdKlrh2WriN-N3FwAy700uzGOnPZRBJIzVRgRlS4WM5tNDM50oTTYWfXrL-zMbeX_6q2GljLraPyzzFgO2IcuOVyn_ukq552--cHJlxkAshOifrQ4Fgs-6jpaDnJL5B7N01qF0E8NrRYKVV_7cFesOQnl-jTnAhFd_0PSeb1JaN7Xdu_B1Nw_BrdX047rEzqUUXZqIHcT4b1ZLZ8OX0G-L7icyyZVS-k5WORA5HKzQTMGPubvTdG-HZVj0yOwz4Yh0bBA",
        'Content-Type': "text/plain"
    }
    lang = {"language": "en"}
    response = requests.post("https://emsiservices.com/skills/versions/latest/extract", keyword, headers=headers, params=lang)
    data = response.json()
    if data.get('data'):
        return [{'description': data['data'][0]['skill']['description']}]
    else:
        return [{'description': "You are on your own."}]
    
# Makes a word cloud
@app.route('/word_cloud', methods=['GET'])
def word_cloud():
    keyword = request.args.get('keyword')
    wordList = getWords(keyword)
    combined_text = ' '.join(wordList)
    wordcloud_image = wordCloud(combined_text)
    return send_file(wordcloud_image, mimetype='image/png')

@app.route('/results', methods=['GET'])
def results():
    keyword = request.args.get('keyword')
    news = getNews(keyword)
    summary = summarize(keyword)
    return render_template('second_page.html', keyword=keyword, news_articles=news, summarized_text=summary[0])

if __name__ == "__main__":
    app.run(debug=True)