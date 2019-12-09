# StockRadar

StockRadar is a **financial news headlines analyser**. It retrieves financial news articles in real-time and decets the most talked about topics and key words in current financial news.



### How does StockRadar work?

#### Stage 1: Web Scraping
Using request, beautifulsoup and regex, the script scrapes the website, parses the HTML and fetches the title and link of all relevant news articles. Then, using regex, textblob and nltk, each news headline is filtered (removing stopwords, singularize) to detect the key words in the headline. Finally the data is stored in a PostgreSQL database in the format [ source, full headline, keywords, date, link ]. The process is tailored to each website to maximize performance.

Currently fetches news from: Reuters, WSJ, Yahoo finance, CNBC finance, Marketwatch, India Times ET, Financel Times, Financial News London, Investing.com, CNN Business.

* Key Skills: Web Scraping, Natural Language Processing, Databases

#### Stage 2: Data Analysis
After the data is fetched and stored in the database, the script queries all recent headlines (currently defined as retreived in the last 3 hours) from the database, then parses all individual words from the headlines and stores them as a list. This list is filtered once again and then analysed for the most frequently-appearing words. The top 15 most common words will appear on the web-app as keywords, while the 3 most common words are marked as topics for second-level analysis - for each topic, the script fetches only articles mentioning the topic and analyses these for the most common keywords given a topic.

* Key Skills: Data Extraction, Frequency Analysis

#### Stage 3: Storing Processed Data

Each keyword is paired with its 'importance' - a metric based on the frequency of each keyword and scaled using linear transformation (from min 40 to max 160) for future front-end display. All processed data is stored in a PostgreSQL table to be later queried for front-end use.

#### Stage 4: Django Framework

All PostgreSQL tables were fitted with a Django model. From a Django view the processed data is queried, and for each keyword a sample of the 6 most recent articles mentioning the keyword will be fetched and stored together with the keyword and its importance as in json format (same goes for each keyword in a topic). The keywords and topics json dictionaries are passed forward to a JavaScript visualisation library using Django's render and the json_tag library.

* Key Skills: Django Framework, MVC Pattern

#### Stage 5: Data Visualisation

Using the D3.js library, all keyword json dictionaries are parsed and displayed as a keyword bubble sized proportionally to the keyword's importance. The visualisation is interactive and responds to both dragging behaviour and click behaviour. The topic json dictionaries are also parsed, however their display is hidden until the user chooses one of the given topics from the scroll-down list. The visualisation can be restored to its original state by clicking the default button.

Clicking a keyword bubble triggers the display of the 6 most recent articles mentioning the chosen keywords. The articles are displayed in a container with the title, time fetched, headline keywords and source stated for each article. The content of the article container changes after clicking a different keyword bubble, or restored to no display when the default button is clicked.

* Key Skills: Front-Back Integration, D3.js Visualisation, Interactive Front-End


*Note: Best viewed on a desktop browser, but is compatible with most mobile devices.*



## License
[MIT](https://choosealicense.com/licenses/mit/)