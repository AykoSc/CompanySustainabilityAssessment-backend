"""
The "NewsSentiment" package has been tested, and has provided mediocre results at best.
However, the code is still left behind to enable future testing.
Installing the package "NewsSentiment" is necessary if you want to try this code out.
"""

from NewsSentiment import TargetSentimentClassifier

tsc = TargetSentimentClassifier()

sentiment = tsc.infer_from_text("", "Volkswagen", " has received backlash over faked emission tests.")
print(sentiment[0])
