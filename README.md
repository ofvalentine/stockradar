# StockRadar

StockRadar is a **financial news headlines analyser**. It retrieves financial news articles in real-time and decets the most talked about topics and key words in current financial news.



### How does StockRadar work?

#### Stage 1: Web Scraping
Using request, beautifulsoup and regex, the script scrapes the website, parses the HTML and fetches the title and link of all relevant news articles. Then, using regex, textblob and nltk, each news headline is filtered (removing stopwords, singularize) to detect the key words in the headline. Finally the data is stored in a PostgreSQL database in the format [ source, full headline, keywords, date, link ]. The process is tailored to each website to maximize performance.

Currently fetches news from: Reuters, WSJ, Yahoo finance, CNBC finance, Marketwatch, India Times ET, Financel Times, Financial News London, Investing.com, CNN Business.

* Languages used: Python, PostgreSQL
* Libraries used: psycopg2, BeautifulSoup, requests, re, textblob, nltk
* Key topics: web scraping, natural language processing

#### Stage 2: Data Analysis
