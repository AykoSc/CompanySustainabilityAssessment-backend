"""
This script can be used to compare different models for sentiment analysis.
Some pre-existing news headlines exist already, as well as URLs to three popular models on huggingface.
"""

from torch.nn import Softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class SentimentAnalyzer:
    MODEL_HUGGINGFACE_URL_TWITTER = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    MODEL_HUGGINGFACE_URL_GENERIC = "Seethal/sentiment_analysis_generic_dataset"
    MODEL_HUGGINGFACE_URL_FINBERT = "ProsusAI/finbert"

    @staticmethod
    def convert_to_rating_positive_negative_neutral(probabilities: list[float]) -> float:
        """
        Converts a 3-point sentiment (positive, negative, neutral) into a sentiment rating from 0 to 10,
        where 0 is negative, 5 is neutral, and 10 is positive.

        :param probabilities: 3-point sentiment (positive, negative, neutral)
        :return: Sentiment rating from 0 to 10
        """
        negative_weight = 0
        neutral_weight = 5
        positive_weight = 10

        rating = (probabilities[0] * positive_weight +
                  probabilities[1] * negative_weight +
                  probabilities[2] * neutral_weight)
        return rating

    @staticmethod
    def analyze_sentiment(text: str, huggingface_url: str) -> float:
        """
        Analyzes the sentiment of a given text using the given model.
        :param text: Text to analyze
        :param huggingface_url: The URL on huggingface where the model lies at
        :return: Sentiment in the range 0-10, with 0 being negative, 5 neutral, and 10 positive.
        """
        # Use model from Hugging Face
        tokenizer = AutoTokenizer.from_pretrained(huggingface_url)
        model = AutoModelForSequenceClassification.from_pretrained(huggingface_url)

        tokens = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)

        outputs = model(**tokens)

        logits = outputs.logits

        softmax = Softmax(dim=1)
        probabilities = softmax(logits)[0].tolist()

        return SentimentAnalyzer.convert_to_rating_positive_negative_neutral(probabilities)


if __name__ == "__main__":
    news_headlines = [
        "Apple: Red Flags Everywhere (NASDAQ:AAPL) - Seeking Alpha",
        "Philly cops brawl with masked looters after they ransacked Footlocker, Apple and Lululemon before making "
        "TWENT - Daily Mail",
        "China lists mobile app stores that comply with new rule, but Apple ... - Reuters",
        "Some Apple iPhone 15 Pro owners complain their new devices get too hot to touch while gaming or video "
        "chatting: ‘It’s burning up’ - Fortune",
        "Apple Releases iOS 17.0.2 and iPadOS 17.0.2 for All iPhones and ... - MacRumors",
        "iPhone wars: India's Apple crop sparks an Indo-China social media battle - The Economic Times",
        "Women's Soccer Travels to the Big Apple for Ivy League Clash with ... - Harvard Athletics",
        "Gurman: October Apple Event Unlikely, Upcoming iPad Air Refresh ... - MacRumors",
        "macOS Sonoma is available today - Apple",
        "Apple Delays Newest Processor Rollout -- Is Taiwan Semi Manufacturing in Deep Trouble? - The Motley Fool",
        "Apple introduces global developer resource for labs, sessions, and ... - Apple",
        "How to View Your UK Bank Account Balance and Deposits in Apple Wallet - MacRumors",
        "Is Apple Stock a Buy Now? - The Motley Fool",
        "Thursday's top Wall Street analyst calls include Apple - CNBC",
        "Apple Now Selling Refurbished 2023 Mac Studio Models - MacRumors",
        "Apple iPhone 15 Pro Overheating Reports: Insider Addresses Issue - Forbes",
        "Over 100 new podcasts from top apps and services launch on Apple ... - Apple",
        "Apple’s M1 MacBook Air is back down to its all-time low price - CNN Underscored",
        "Apple asks US Supreme Court to strike down Epic Games order - Reuters",
        "Apple is ordered to face Apple Pay antitrust lawsuit - Reuters",
        "iPhone 15 and iPhone 15 Plus - Apple",
        "How Apple could be affected by Amazon's antitrust ruling - Yahoo Finance",
        "Apple Seeds First Betas of iOS 17.1 and iPadOS 17.1 to Developers - MacRumors",
        "Apple will have to face an antitrust lawsuit alleging iOS Apple Pay dominance - The Verge",
        "Kuo: Development of Apple Car Has 'Lost All Visibility' - MacRumors",
        "How Microsoft could supplant Apple as the world's most valuable firm - The Economist",
        "Apple unveils iPhone 15 Pro and iPhone 15 Pro Max - Apple",
        "Microsoft Says Apple Used Bing as Google 'Bargaining Chip' - Bloomberg",
        "Apple leverages idea of switching to Bing to pry more money out of Google, Microsoft exec says - ABC News",
        "Philadelphia swarmed by alleged juvenile looters targeting the Apple Store, Lululemon, Footlocker and others "
        "- Fox News",
        "iPhone 15 lineup and new Apple Watch lineup arrive worldwide - Apple",
        "Epic asks the Supreme Court to weigh in on its beef with Apple - TechCrunch",
        "iOS 17 is available today - Apple",
        "EU's Breton tells Apple CEO to open its ecosystem to rivals - Reuters",
        "Apple mental health features: How to log your mood - Mashable",
        "Apple’s iPhone Cedes Ground to Google’s Pixel in Japan - Yahoo Finance",
        "Yale Launches Apple Home Key-Enabled Assure Lock 2 Plus - MacRumors",
        "watchOS 10 is available today - Apple",
        "Can the iPhone 15 Help Reverse Apple's Sales Decline? - The Motley Fool",
        "Apple Suggests Potential Fixes for Weather Complication Bug on ... - MacRumors",
        "The Apple Watch Series 8 just hit an all-time low price - CNN Underscored",
        "Environment - Mother Nature - Apple",
        "Apple's long-term demand for 3nm chips may be lower than expected - AppleInsider",
        "Best USB-C charger cable for Apple's new iPhone 15 - USA TODAY",
        "Apple Watch Series 9 review: Upgrade for this key feature (no, it's ... - Mashable",
        "Summer's Spotlight: Four Flags Area Apple Festival returns for 2023 ... - ABC 57 News",
        "Meta Debuts $500 Quest 3 as Apple Prepares to Launch $3500 ... - MacRumors",
        "Apple removes app created by Andrew Tate - The Guardian",
        "Apple Releases Security Updates for Multiple Products - CISA",
        "Apple Might Cancel Entry-Level Vision Pro, Analyst Says - ExtremeTech",
        "Baskin-Robbins adds Apple Cider Donut as October flavor of the ... - USA TODAY",
        "New Apple Leak Highlights Unexpected MacBook Pro Choice - Forbes",
        "Apple May Be Planning to Discontinue All of Its Silicone Accessories - MacRumors",
        "Apple announces next Impact Accelerator class advancing ... - Apple",
        "Apple to Launch 'Low-Cost' MacBook Series Next Year to Rival ... - MacRumors",
        "Apple disputes French findings, says iPhone 12 meets radiation rules - Reuters",
        "Apple Answers of All Our iPhone 15 Pro Questions: 'It's Going to be ... - IGN",
        "Apple's failure to develop its own modem detailed in new report - The Verge",
        "Apple's Decision to Kill Its CSAM Photo-Scanning Tool Sparks Fresh ... - WIRED",
        "Apple Unveils iPhone 15 With Changes to Its USB-C Charger - The New York Times",
        "Apple Event 2023: Everything you need to know about iPhone 15, Apple Watch, USB-C connector - TechCrunch",
        "Apple lost $200 billion in two days after reports of iPhone ban in China - CNN",
        "Apple's Stock Is Having a Rough Week - The Wall Street Journal",
        "What to Expect From Apple's September 12 Event: iPhone 15, Apple ... - MacRumors",
        "Apple's M3 MacBooks might not arrive this year - The Verge",
        "Apple's $60 iCloud Service Is the Future of Apple - WIRED",
        "Apple and Goldman were planning stock-trading feature for iPhones until markets turned last year - CNBC",
        "Qualcomm says it will supply Apple with 5G modems for iPhones through 2026 - CNBC",
        "Apple zero-click iMessage exploit used to infect iPhones with spyware - BleepingComputer",
        "Apple Watch Series 9: Apple (AAPL) Tests 3D Printing in Device ... - Bloomberg",
        "Apple Plans to Stop Providing Customer Support on Twitter and ... - MacRumors",
        "Apple launches new ‘Apps by Apple’ website, promoting its ... - 9to5Mac",
        "Apple inks new long-term deal with Arm for chip technology ... - Reuters",
        "Apple's Ridiculously Simple Strategy to Beat Burnout Is Oddly ... - Inc.",
        "iPhone Mini Might Be Discontinued Following Apple Event This ... - MacRumors",
        "Apple Announces 'Wonderlust' Event Expected to Feature iPhone 15 ... - MacRumors",
        "Messi Drives Jump in Apple TV+ and MLS Subscriptions - WSJ - The Wall Street Journal",
        "Apple and Microsoft fight Brussels over 'gatekeeper' label for ... - Financial Times",
        "Apple Leak Details All-New iPhone 15, iPhone 15 Pro Price Changes - Forbes",
        "iPhone 15, iPhone 15 Pro Release Problems Hit Apple’s New iPhones - Forbes",
        "Apple Boosts Spending to Develop Conversational AI - The Information",
        "Renamed 'Apple Payments Services' Company Likely Behind New ... - MacRumors",
        "Apple introduces global developer resource for labs, sessions, and workshops - Apple",
        "Over 100 new podcasts from top apps and services launch on Apple Podcasts - Apple",
        "Apple will have to face an antitrust lawsuit alleging iOS Apple Pay ... - The Verge",
        "iPhone 15 Pro review: Apple delivers the Action you didn’t know you needed - CNN Underscored",
        "Apple expands the power of iCloud with new iCloud+ plans - Apple",
        "Apple offers more ways to order the all-new iPhone 15 and Apple Watch lineups - Apple",
        "Apple introduces the advanced new Apple Watch Series 9 - Apple",
        "Apple Delays Newest Processor Rollout -- Is Taiwan Semi ... - The Motley Fool",
        "Apple (AAPL) iPhone 15 Pro and Max Get Too Hot While Using, Charging, Users Say - Bloomberg",
        "iPhone 15 Pro and iPhone 15 Pro Max - Apple",
        "Biogen shutters digital health group, nixes Apple study, as part of ... - STAT",
        "Apple Watch Series 9 - Apple",
        "Speer Elementary School teacher receives CBS News Texas Crystal Apple Award - CBS News",
        "Apple unveils its first carbon neutral products - Apple",
        "Apple and Google are changing the way we listen to podcasts - The Verge",
        "Watch - 'Philadelphia Has Fallen': Teens Loot US Apple Store In Mad Frenzy - NDTV",
        "This Old-Fashioned Apple Peeler Is the Best Way to Peel Apples - The New York Times",
        "Apple Wallet app can now show current account balances from UK banks - 9to5Mac",
        "Apple Prepares To Delay MacBook Air To Find iPhone Success - Forbes",
        "Apple Releases Security Updates for iOS and macOS - CISA",
        "Apple iPhone 15 Release Date: New Event Page Goes Live With Cool Animation - Forbes",
        "Apple Apparently 'Got Close' to Launching a 14-Inch iPad This Year - MacRumors",
        "'Apple Payments Services' Company Likely Behind New Apple Wallet Features in UK, Potentially More to Follow "
        "- MacRumors",
        "Golden Apple Award: Spotlight on an unsung hero - KOLN",
        "Top Apple Executive Defends Favoring Google on iPhones - The New York Times",
        "Not a Fan of Apple's Latest Contact-Sharing Feature? Here's How ... - CNET"
    ]

    output = "\nErfolgte Analyse:"
    for text in news_headlines:
        output = f"Text: {text:<50}"
        output += (f"\n    Finbert: "
                   f"{SentimentAnalyzer.analyze_sentiment(text, SentimentAnalyzer.MODEL_HUGGINGFACE_URL_FINBERT)}")

        print(output)
