"""
Advanced Natural Language Understanding module for Email Management AI Agent.
Improves comprehension of complex email content to better extract meaning and requirements.
"""

import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import string
from collections import defaultdict

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

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except:
    # If model not found, download it
    import os
    os.system("python -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")

class AdvancedNLPUnderstanding:
    """
    Handles advanced natural language understanding for complex email content.
    """
    
    def __init__(self):
        """
        Initialize the advanced NLP understanding system.
        """
        # Initialize NLP components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Multi-part request patterns
        self.request_indicators = [
            r'(?:please|kindly|could you|can you|would you)\s+(.+?)[\.;,]',
            r'(?:need|want|require)\s+you\s+to\s+(.+?)[\.;,]',
            r'(?:would|should)\s+(?:like|appreciate)\s+(?:it\s+)?if\s+you\s+(?:could|would)\s+(.+?)[\.;,]',
            r'(?:I\'m|I am)\s+(?:asking|requesting)\s+(?:you\s+)?to\s+(.+?)[\.;,]',
            r'(?:hoping|hope)\s+(?:you\s+)?(?:can|could|will|would)\s+(.+?)[\.;,]'
        ]
        
        # List markers for multi-part requests
        self.list_markers = [
            r'^\s*(\d+\.|\d+\)|\*|\-|\•)\s+',  # Numbered or bullet points
            r'(?:first(?:ly)?|1st|one)[,:\s]\s*(.+?)[\.;,]',
            r'(?:second(?:ly)?|2nd|two)[,:\s]\s*(.+?)[\.;,]',
            r'(?:third(?:ly)?|3rd|three)[,:\s]\s*(.+?)[\.;,]',
            r'(?:fourth(?:ly)?|4th|four)[,:\s]\s*(.+?)[\.;,]',
            r'(?:fifth(?:ly)?|5th|five)[,:\s]\s*(.+?)[\.;,]',
            r'(?:finally|lastly|last)[,:\s]\s*(.+?)[\.;,]'
        ]
        
        # Conditional request patterns
        self.conditional_patterns = [
            r'if\s+(.+?),\s+(?:please|kindly|could you|can you|would you)\s+(.+?)[\.;,]',
            r'(?:please|kindly|could you|can you|would you)\s+(.+?)\s+if\s+(.+?)[\.;,]',
            r'(?:assuming|provided|given)\s+that\s+(.+?),\s+(.+?)[\.;,]',
            r'(?:once|after|when)\s+(.+?),\s+(?:please|kindly|could you|can you|would you)\s+(.+?)[\.;,]',
            r'(?:depending|based)\s+on\s+(.+?),\s+(.+?)[\.;,]'
        ]
        
        # Reference resolution patterns
        self.reference_patterns = {
            'pronoun': [
                r'\b(it|this|that|these|those|they|them|their)\b',
                r'\b(he|him|his|she|her|hers)\b'
            ],
            'temporal': [
                r'\b(yesterday|today|tomorrow)\b',
                r'\b(last|this|next)\s+(week|month|year|quarter)\b',
                r'\b(previous|current|upcoming)\s+(week|month|year|quarter)\b'
            ],
            'document': [
                r'\b(attached|attachment|document|file|spreadsheet|presentation)\b',
                r'\b(report|analysis|proposal|plan|draft|version)\b'
            ]
        }
        
        # Domain-specific terminology (to be expanded based on user's industry)
        self.domain_terminology = {
            'general_business': {
                'KPI': 'Key Performance Indicator',
                'ROI': 'Return on Investment',
                'EOD': 'End of Day',
                'COB': 'Close of Business',
                'EOM': 'End of Month',
                'EOY': 'End of Year',
                'OKR': 'Objectives and Key Results',
                'ASAP': 'As Soon As Possible',
                'FYI': 'For Your Information',
                'TL;DR': 'Too Long; Didn\'t Read (Summary)',
                'WFH': 'Work From Home',
                'OOO': 'Out of Office',
                'NDA': 'Non-Disclosure Agreement',
                'SOW': 'Statement of Work',
                'EOB': 'End of Business',
                'QBR': 'Quarterly Business Review'
            },
            'tech': {
                'PR': 'Pull Request',
                'LGTM': 'Looks Good To Me',
                'WIP': 'Work In Progress',
                'POC': 'Proof of Concept',
                'MVP': 'Minimum Viable Product',
                'UAT': 'User Acceptance Testing',
                'QA': 'Quality Assurance',
                'CI/CD': 'Continuous Integration/Continuous Deployment',
                'API': 'Application Programming Interface',
                'UI/UX': 'User Interface/User Experience',
                'SLA': 'Service Level Agreement',
                'TOS': 'Terms of Service'
            },
            'finance': {
                'P&L': 'Profit and Loss',
                'EBITDA': 'Earnings Before Interest, Taxes, Depreciation, and Amortization',
                'YOY': 'Year Over Year',
                'QOQ': 'Quarter Over Quarter',
                'MOM': 'Month Over Month',
                'AR': 'Accounts Receivable',
                'AP': 'Accounts Payable',
                'CAPEX': 'Capital Expenditure',
                'OPEX': 'Operational Expenditure',
                'FCF': 'Free Cash Flow'
            },
            'marketing': {
                'CTR': 'Click-Through Rate',
                'CPC': 'Cost Per Click',
                'CPM': 'Cost Per Mille (Cost Per Thousand Impressions)',
                'CTA': 'Call To Action',
                'SEO': 'Search Engine Optimization',
                'SEM': 'Search Engine Marketing',
                'PPC': 'Pay Per Click',
                'CR': 'Conversion Rate',
                'USP': 'Unique Selling Proposition',
                'KOL': 'Key Opinion Leader'
            }
        }
        
        # Organizational acronyms (to be populated from user data)
        self.org_acronyms = {}
        
        # Context window for reference resolution
        self.context_window = []
        self.max_context_size = 5  # Maximum number of emails in context window
    
    def analyze_email(self, email, thread_context=None):
        """
        Analyze email content with advanced NLP understanding.
        
        Args:
            email (dict): Email data
            thread_context (list, optional): Previous emails in the thread
            
        Returns:
            dict: Analysis results
        """
        # Extract email content
        subject = email.get('subject', '')
        body = email.get('body', '')
        sender = email.get('sender', '')
        
        # Update context window
        self._update_context_window(email, thread_context)
        
        # Process email with spaCy
        doc = nlp(f"{subject}\n\n{body}")
        
        # Extract multi-part requests
        requests = self._extract_requests(body, doc)
        
        # Extract conditions and dependencies
        conditions = self._extract_conditions(body, doc)
        
        # Resolve references
        resolved_references = self._resolve_references(body, doc)
        
        # Identify domain-specific terminology
        terminology = self._identify_terminology(body)
        
        # Extract entities
        entities = self._extract_entities(doc)
        
        # Analyze syntactic complexity
        complexity = self._analyze_complexity(doc)
        
        # Create analysis result
        analysis = {
            'requests': requests,
            'conditions': conditions,
            'resolved_references': resolved_references,
            'terminology': terminology,
            'entities': entities,
            'complexity': complexity,
            'summary': self._generate_summary(requests, conditions, resolved_references, terminology, entities, complexity)
        }
        
        return analysis
    
    def _update_context_window(self, email, thread_context=None):
        """
        Update context window with current email and thread context.
        
        Args:
            email (dict): Current email
            thread_context (list, optional): Previous emails in the thread
        """
        # Add current email to context window
        self.context_window.append(email)
        
        # Add thread context if provided
        if thread_context:
            for context_email in thread_context:
                if context_email not in self.context_window:
                    self.context_window.append(context_email)
        
        # Limit context window size
        if len(self.context_window) > self.max_context_size:
            self.context_window = self.context_window[-self.max_context_size:]
    
    def _extract_requests(self, text, doc):
        """
        Extract requests from email text.
        
        Args:
            text (str): Email text
            doc (spacy.Doc): Processed spaCy document
            
        Returns:
            list: Extracted requests
        """
        requests = []
        
        # Extract explicit requests using patterns
        for pattern in self.request_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                request_text = match.group(1).strip()
                if request_text and len(request_text) > 5:  # Minimum length to filter out noise
                    requests.append({
                        'text': request_text,
                        'type': 'explicit',
                        'confidence': 0.9
                    })
        
        # Extract list-based requests
        list_items = self._extract_list_items(text)
        for item in list_items:
            # Check if item looks like a request
            if any(re.search(pattern, item, re.IGNORECASE) for pattern in self.request_indicators):
                requests.append({
                    'text': item,
                    'type': 'list_item',
                    'confidence': 0.8
                })
            elif any(verb in item.lower() for verb in ['send', 'review', 'update', 'create', 'check', 'prepare', 'provide']):
                requests.append({
                    'text': item,
                    'type': 'implied',
                    'confidence': 0.7
                })
        
        # Extract implicit requests using spaCy
        for sent in doc.sents:
            # Check if sentence contains imperative verbs
            if self._is_imperative(sent) and sent.text not in [r['text'] for r in requests]:
                requests.append({
                    'text': sent.text,
                    'type': 'imperative',
                    'confidence': 0.6
                })
        
        # Deduplicate requests
        unique_requests = []
        seen_texts = set()
        
        for request in requests:
            # Normalize text for comparison
            normalized = ' '.join(request['text'].lower().split())
            
            # Check if similar request already exists
            if not any(self._is_similar_text(normalized, seen) for seen in seen_texts):
                unique_requests.append(request)
                seen_texts.add(normalized)
        
        return unique_requests
    
    def _extract_list_items(self, text):
        """
        Extract list items from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: Extracted list items
        """
        list_items = []
        
        # Split text into lines
        lines = text.split('\n')
        
        # Extract numbered and bulleted list items
        for line in lines:
            line = line.strip()
            if re.match(r'^\s*(\d+\.|\d+\)|\*|\-|\•)\s+', line):
                # Remove the list marker
                item = re.sub(r'^\s*(\d+\.|\d+\)|\*|\-|\•)\s+', '', line)
                list_items.append(item)
        
        # Extract sequential markers (first, second, etc.)
        for pattern in self.list_markers[1:]:  # Skip the first pattern which is for bullet points
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                item = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
                list_items.append(item)
        
        return list_items
    
    def _is_imperative(self, sent):
        """
        Check if a sentence is in imperative form.
        
        Args:
            sent (spacy.Span): Sentence to check
            
        Returns:
            bool: True if imperative, False otherwise
        """
        # Imperative sentences often start with a verb
        if len(sent) > 0 and sent[0].pos_ == 'VERB':
            return True
        
        # Or they might start with 'Please' followed by a verb
        if len(sent) > 1 and sent[0].text.lower() == 'please' and sent[1].pos_ == 'VERB':
            return True
        
        # Check for other imperative indicators
        imperative_starters = ['kindly', 'please', 'ensure', 'make sure', 'remember']
        if any(sent.text.lower().startswith(starter) for starter in imperative_starters):
            return True
        
        return False
    
    def _is_similar_text(self, text1, text2, threshold=0.7):
        """
        Check if two texts are similar.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            threshold (float): Similarity threshold
            
        Returns:
            bool: True if similar, False otherwise
        """
        # Simple Jaccard similarity
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return False
        
        similarity = intersection / union
        return similarity >= threshold
    
    def _extract_conditions(self, text, doc):
        """
        Extract conditions and dependencies from text.
        
        Args:
            text (str): Email text
            doc (spacy.Doc): Processed spaCy document
            
        Returns:
            list: Extracted conditions
        """
        conditions = []
        
        # Extract explicit conditions using patterns
        for pattern in self.conditional_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    condition_text = match.group(1).strip()
                    action_text = match.group(2).strip()
                    
                    conditions.append({
                        'condition': condition_text,
                        'action': action_text,
                        'type': 'explicit',
                        'confidence': 0.9
                    })
        
        # Extract implicit conditions using spaCy
        for sent in doc.sents:
            # Look for conditional markers
            if any(token.text.lower() in ['if', 'when', 'once', 'after', 'before', 'unless', 'until'] for token in sent):
                # Skip if already captured by explicit patterns
                if not any(cond['condition'] in sent.text and cond['action'] in sent.text for cond in conditions):
                    # Try to split into condition and action
                    condition_parts = self._split_conditional(sent.text)
                    if condition_parts:
                        conditions.append({
                            'condition': condition_parts[0],
                
(Content truncated due to size limit. Use line ranges to read in chunks)