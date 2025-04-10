"""
Email summarization module for generating concise email summaries.
"""

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist

class EmailSummarizer:
    """
    Handles summarization of email content.
    """
    
    def __init__(self):
        """
        Initialize the email summarizer.
        """
        # Download required NLTK resources
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
    
    def summarize_email(self, email, max_sentences=3):
        """
        Generate a concise summary of an email.
        
        Args:
            email (dict): Email data to summarize
            max_sentences (int): Maximum number of sentences in the summary
            
        Returns:
            dict: Email with added summary
        """
        # Make a copy of the email to avoid modifying the original
        summarized_email = email.copy()
        
        # Get email body text
        body = email.get('body', '')
        
        # If body is empty or not a string, use snippet
        if not body or not isinstance(body, str):
            body = email.get('snippet', '')
            
        # If still no content, return with empty summary
        if not body:
            summarized_email['summary'] = "No content to summarize."
            return summarized_email
        
        # Clean the text
        clean_text = self._clean_text(body)
        
        # Generate summary
        summary = self._extract_summary(clean_text, max_sentences)
        
        # Add summary to email
        summarized_email['summary'] = summary
        
        return summarized_email
    
    def _clean_text(self, text):
        """
        Clean and preprocess the text for summarization.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove email signatures (common patterns)
        text = re.sub(r'--+\s*\n.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Best regards,.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Regards,.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Thanks,.*', '', text, flags=re.DOTALL)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_summary(self, text, max_sentences):
        """
        Extract a summary from the text using extractive summarization.
        
        Args:
            text (str): Text to summarize
            max_sentences (int): Maximum number of sentences in the summary
            
        Returns:
            str: Summary text
        """
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        
        # If there are fewer sentences than max_sentences, return the whole text
        if len(sentences) <= max_sentences:
            return text
        
        # Tokenize words and remove stop words
        words = [word.lower() for word in word_tokenize(text) if word.isalnum() and word.lower() not in self.stop_words]
        
        # Calculate word frequencies
        freq_dist = FreqDist(words)
        
        # Score sentences based on word frequencies
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            for word in word_tokenize(sentence.lower()):
                if word in freq_dist:
                    score += freq_dist[word]
            sentence_scores[i] = score
        
        # Get the top N sentences with highest scores
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # Sort sentences by their original order
        top_sentences = sorted(top_sentences, key=lambda x: x[0])
        
        # Construct the summary
        summary = ' '.join([sentences[i] for i, _ in top_sentences])
        
        return summary
    
    def generate_key_points(self, email, max_points=3):
        """
        Extract key points from an email.
        
        Args:
            email (dict): Email data
            max_points (int): Maximum number of key points to extract
            
        Returns:
            list: List of key points
        """
        # Get email body text
        body = email.get('body', '')
        
        # If body is empty or not a string, use snippet
        if not body or not isinstance(body, str):
            body = email.get('snippet', '')
            
        # If still no content, return empty list
        if not body:
            return []
        
        # Clean the text
        clean_text = self._clean_text(body)
        
        # Tokenize into sentences
        sentences = sent_tokenize(clean_text)
        
        # Look for sentences that might contain key information
        key_indicators = [
            'important', 'key', 'main', 'critical', 'essential',
            'please note', 'remember', 'don\'t forget', 'action required',
            'deadline', 'due date', 'summary'
        ]
        
        key_points = []
        
        # First pass: look for sentences with key indicators
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in key_indicators):
                key_points.append(sentence)
                if len(key_points) >= max_points:
                    break
        
        # Second pass: if we don't have enough key points, add the first few sentences
        if len(key_points) < max_points:
            for sentence in sentences:
                if sentence not in key_points:
                    key_points.append(sentence)
                    if len(key_points) >= max_points:
                        break
        
        return key_points
