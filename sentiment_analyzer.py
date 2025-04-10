"""
Sentiment Analysis module for Email Management AI Agent.
Detects emotional tone and urgency in emails.
"""

import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class SentimentAnalyzer:
    """
    Handles detection of emotional tone and urgency in emails.
    """
    
    def __init__(self):
        """
        Initialize the sentiment analyzer.
        """
        # Initialize NLP components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Emotion dictionaries
        self.emotion_lexicon = {
            'frustration': [
                'frustrated', 'annoyed', 'irritated', 'upset', 'disappointed', 
                'dissatisfied', 'unhappy', 'displeased', 'bothered', 'troubled',
                'aggravated', 'agitated', 'exasperated', 'fed up', 'impatient',
                'problem', 'issue', 'concern', 'difficulty', 'challenge',
                'struggle', 'fail', 'failed', 'failure', 'mistake', 'error',
                'wrong', 'incorrect', 'not working', 'doesn\'t work', 'broken'
            ],
            'satisfaction': [
                'satisfied', 'pleased', 'happy', 'glad', 'delighted', 
                'content', 'grateful', 'thankful', 'appreciative', 'impressed',
                'excellent', 'great', 'good', 'wonderful', 'fantastic',
                'amazing', 'outstanding', 'exceptional', 'perfect', 'brilliant',
                'superb', 'terrific', 'awesome', 'impressive', 'splendid',
                'success', 'successful', 'achievement', 'accomplish', 'achieved'
            ],
            'urgency': [
                'urgent', 'immediately', 'asap', 'as soon as possible', 'right away',
                'quickly', 'promptly', 'expedite', 'rush', 'hurry', 'swift',
                'critical', 'crucial', 'vital', 'essential', 'important',
                'priority', 'time-sensitive', 'deadline', 'due', 'emergency',
                'pressing', 'imperative', 'now', 'today', 'soon',
                'cannot wait', 'can\'t wait', 'without delay', 'at once'
            ],
            'appreciation': [
                'thank', 'thanks', 'thank you', 'grateful', 'appreciate',
                'appreciation', 'thankful', 'gratitude', 'indebted', 'obliged',
                'recognition', 'acknowledged', 'valued', 'admire', 'admiration',
                'impressed', 'impressive', 'excellent', 'outstanding', 'exceptional',
                'wonderful', 'fantastic', 'great', 'good', 'helpful',
                'supportive', 'assistance', 'support', 'help', 'aided'
            ],
            'concern': [
                'concerned', 'worry', 'worried', 'anxious', 'uneasy',
                'apprehensive', 'troubled', 'disturbed', 'distressed', 'alarmed',
                'fear', 'afraid', 'scared', 'frightened', 'terrified',
                'nervous', 'tense', 'stressed', 'stress', 'pressure',
                'uncertain', 'unsure', 'doubt', 'doubtful', 'hesitant',
                'risk', 'risky', 'dangerous', 'threat', 'threatening'
            ],
            'confusion': [
                'confused', 'confusing', 'unclear', 'ambiguous', 'vague',
                'puzzled', 'perplexed', 'bewildered', 'baffled', 'lost',
                'misunderstood', 'misunderstanding', 'miscommunication', 'mistake', 'error',
                'uncertain', 'unsure', 'doubt', 'question', 'wondering',
                'clarify', 'clarification', 'explain', 'explanation', 'understand'
            ]
        }
        
        # Urgency indicators with weights
        self.urgency_indicators = {
            'immediate': [
                ('urgent', 5), ('emergency', 5), ('asap', 5), ('immediately', 5), ('right away', 5),
                ('right now', 5), ('as soon as possible', 4), ('critical', 4), ('crucial', 4),
                ('without delay', 4), ('at once', 4), ('time sensitive', 4), ('time-sensitive', 4)
            ],
            'today': [
                ('today', 3), ('by end of day', 4), ('by close of business', 4), ('cob', 4),
                ('eod', 4), ('this morning', 3), ('this afternoon', 3), ('this evening', 3),
                ('within hours', 4), ('few hours', 3), ('couple of hours', 3)
            ],
            'tomorrow': [
                ('tomorrow', 2), ('next day', 2), ('by tomorrow', 3), ('within 24 hours', 3),
                ('24 hours', 3), ('one day', 2), ('1 day', 2)
            ],
            'this_week': [
                ('this week', 1), ('within days', 2), ('few days', 1), ('couple of days', 1),
                ('by friday', 2), ('before weekend', 2), ('within 48 hours', 2), ('48 hours', 2)
            ]
        }
        
        # Passive-aggressive phrases
        self.passive_aggressive_phrases = [
            'as per my last email', 'as stated previously', 'as mentioned before',
            'as I said earlier', 'as already discussed', 'as noted above',
            'per my previous email', 'refer to my previous message', 'reattaching for convenience',
            'friendly reminder', 'just a reminder', 'gentle reminder',
            'for the second time', 'once again', 'to repeat myself',
            'circling back', 'following up again', 'checking in again',
            'not sure if you saw', 'in case you missed', 'perhaps you overlooked',
            'I thought I was clear', 'to clarify', 'to be clear',
            'going forward', 'moving forward', 'in the future',
            'please advise', 'kindly advise', 'let me know if you need anything else',
            'thanks in advance', 'I appreciate your prompt response', 'at your earliest convenience'
        ]
        
        # Stress indicators
        self.stress_indicators = [
            'overwhelmed', 'stressed', 'pressure', 'overloaded', 'swamped',
            'too much', 'excessive', 'burden', 'stressful', 'demanding',
            'difficult', 'challenging', 'hard', 'tough', 'struggling',
            'exhausted', 'tired', 'fatigue', 'burnout', 'worn out',
            'anxious', 'anxiety', 'worried', 'concern', 'fear',
            'deadline', 'time constraint', 'running out of time', 'behind schedule', 'late',
            'urgent', 'emergency', 'crisis', 'critical', 'crucial',
            'workload', 'backlog', 'pile up', 'accumulate', 'mounting'
        ]
        
        # Relationship indicators
        self.relationship_indicators = {
            'positive': [
                'thank', 'thanks', 'appreciate', 'grateful', 'helpful',
                'support', 'assist', 'collaboration', 'teamwork', 'partnership',
                'excellent', 'great', 'good', 'wonderful', 'fantastic',
                'pleasure', 'enjoy', 'delighted', 'happy', 'glad',
                'impressive', 'impressed', 'admire', 'respect', 'value'
            ],
            'negative': [
                'disappoint', 'frustrat', 'annoy', 'irritate', 'upset',
                'concern', 'worry', 'anxious', 'nervous', 'stress',
                'delay', 'late', 'miss', 'fail', 'error',
                'mistake', 'problem', 'issue', 'difficult', 'challenge',
                'disagree', 'conflict', 'dispute', 'argument', 'tension'
            ],
            'neutral': [
                'inform', 'update', 'advise', 'notify', 'tell',
                'share', 'provide', 'send', 'forward', 'attach',
                'request', 'ask', 'inquire', 'question', 'query',
                'schedule', 'arrange', 'organize', 'coordinate', 'plan',
                'discuss', 'talk', 'speak', 'conversation', 'meeting'
            ]
        }
    
    def analyze_sentiment(self, email):
        """
        Analyze sentiment in an email.
        
        Args:
            email (dict): Email data
            
        Returns:
            dict: Sentiment analysis results
        """
        # Extract email content
        subject = email.get('subject', '')
        body = email.get('body', '')
        sender = email.get('sender', '')
        
        # Combine subject and body for analysis
        text = f"{subject}\n{body}"
        
        # Preprocess text
        preprocessed_text = self._preprocess_text(text)
        
        # Detect emotions
        emotions = self._detect_emotions(preprocessed_text)
        
        # Assess urgency
        urgency = self._assess_urgency(text)
        
        # Detect passive-aggressive tone
        passive_aggressive = self._detect_passive_aggressive(text)
        
        # Detect stress indicators
        stress = self._detect_stress(text)
        
        # Determine overall sentiment
        overall_sentiment = self._determine_overall_sentiment(emotions, urgency, passive_aggressive)
        
        # Create sentiment analysis result
        sentiment_analysis = {
            'overall_sentiment': overall_sentiment,
            'emotions': emotions,
            'urgency': urgency,
            'passive_aggressive': passive_aggressive,
            'stress_indicators': stress,
            'requires_attention': self._requires_attention(emotions, urgency, passive_aggressive, stress)
        }
        
        return sentiment_analysis
    
    def _preprocess_text(self, text):
        """
        Preprocess text for sentiment analysis.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            list: Preprocessed tokens
        """
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        
        # Lemmatize tokens
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def _detect_emotions(self, preprocessed_text):
        """
        Detect emotions in preprocessed text.
        
        Args:
            preprocessed_text (list): Preprocessed tokens
            
        Returns:
            dict: Detected emotions with scores
        """
        # Initialize emotion scores
        emotion_scores = {emotion: 0 for emotion in self.emotion_lexicon.keys()}
        
        # Count emotion words
        for token in preprocessed_text:
            for emotion, words in self.emotion_lexicon.items():
                if token in words or any(word in token for word in words):
                    emotion_scores[emotion] += 1
        
        # Normalize scores
        total_emotions = sum(emotion_scores.values())
        if total_emotions > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = round((emotion_scores[emotion] / len(preprocessed_text)) * 100, 2)
        
        # Get primary and secondary emotions
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        primary_emotion = sorted_emotions[0][0] if sorted_emotions[0][1] > 0 else 'neutral'
        secondary_emotion = sorted_emotions[1][0] if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0 else None
        
        return {
            'primary': primary_emotion,
            'secondary': secondary_emotion,
            'scores': emotion_scores
        }
    
    def _assess_urgency(self, text):
        """
        Assess urgency level in text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Urgency assessment
        """
        # Initialize urgency score
        urgency_score = 0
        matched_indicators = []
        
        # Check for urgency indicators
        text_lower = text.lower()
        for category, indicators in self.urgency_indicators.items():
            for indicator, weight in indicators:
                if re.search(r'\b' + re.escape(indicator) + r'\b', text_lower):
                    urgency_score += weight
                    matched_indicators.append(indicator)
        
        # Determine urgency level
        if urgency_score >= 10:
            urgency_level = 'critical'
        elif urgency_score >= 6:
            urgency_level = 'high'
        elif urgency_score >= 3:
            urgency_level = 'medium'
        elif urgency_score > 0:
            urgency_level = 'low'
        else:
            urgency_level = 'none'
        
        return {
            'level': urgency_level,
            'score': urgency_score,
            'indicators': matched_indicators
        }
    
    def _detect_passive_aggressive(self, text):
        """
        Detect passive-aggressive tone in text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Passive-aggressive assessment
        """
        # Initialize passive-aggressive score
        pa_score = 0
        matched_phrases = []
        
        # Check for passive-aggressive phrases
        text_lower = text.lower()
        for phrase in self.passive_aggressive_phrases:
            if re.search(r'\b' + re.escape(phrase) + r'\b', text_lower):
                pa_score += 1
                matched_phrases.append(phrase)
        
        # Determine passive-aggressive level
        if pa_score >= 3:
            pa_level = 'high'
        elif pa_score >= 1:
            pa_level = 'medium'
        else:
            pa_level = 'none'
        
        return {
            'level': pa_level,
            'score': pa_score,
            'phrases': matched_phrases
        }
    
    def _detect_stress(self, text):
        """
        Detect stress indicators in text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Stress assessment
        """
        # Initialize stress score
        stress_score = 0
        matched_indicators = []
        
        # Check for stress indicators
        text_lower = text.lower()
        for indicator in self.stress_indicators:
            if re.search(r'\b' + re.escape(indicator) + r'\b', text_lower):
                stress_score += 1
                matched_indicators.append(indicator)
        
        # Determine stress level
        if stress_score >= 5:
            stress_level = 'high'
        elif stress_score >= 2:
            stress_level = 'medium'
        elif stress_score >= 1:
            stress_level = 'low'
        else:
            stress_level = 'none'
        
        return {
            'level': stress_level,
            'score': stress_score,
            'indicators': matched_indicators
        }
    
    def _determine_overall_sentiment(self, emotions, urgency, passive_aggressive):
        """
        Determine overall sentiment based on emotions, urgency, and passive-aggressive tone.
        
        Args:
            emotions (dict): Detected emotions
            urgency (dict): Urgency assessment
            passive_aggressive (dict): Passive-aggressive assessment
            
        Returns:
            str: Overall sentiment
        """
        # Get primary emotion
        primary_emotion = emotions['primary']
        
        # Determine sentiment based on primary emotion
        if primary_emotion == 'frustration' or primary_emotion == 'concern':
            sentiment = 'negative'
        elif primary_emotion == 'satisfaction' or primary_emotion == 'appreciation':
            sentiment = 'positive'
        elif primary_emotion == 'confusion':
            sentiment = 'neutral'
        else:
            sentiment = 'neutral'
        
        # Adjust sentiment based on urgency and passive-aggressive tone
        i
(Content truncated due to size limit. Use line ranges to read in chunks)