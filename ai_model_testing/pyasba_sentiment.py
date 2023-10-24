"""
The "pyabsa" package has been tested, and has provided mediocre results at best.
However, the code is still left behind to enable future testing.
Installing the package "pyabsa" is necessary if you want to try this code out.
"""

from pyabsa import AspectPolarityClassification as APC

sentiment_classifier = APC.SentimentClassifier("multilingual")

old_text = "The [B-ASP]food[E-ASP] is good, but the [B-ASP]service[E-ASP] is bad."
text = "Many of [B-ASP]Volkswagen[E-ASP]'s parts are being manufactured by children."

prediction = sentiment_classifier.predict(text)

print("Hier das Ergebnis:")
print(prediction)
