from textblob import TextBlob
blob = TextBlob("We must silence dissent to restore order.")
print(blob.sentiment)
# Output: Sentiment(polarity=-0.5, subjectivity=0.6)
