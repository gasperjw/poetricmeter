import streamlit as st
import re
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

class ArabicMeterAnalyzer:
    def __init__(self):
        # Basic taf'ilat (التفعيلات) and their variations
        self.tafilat = {
            'فعولن': ['فعولن', 'فعول', 'فعو'],
            'مفاعيلن': ['مفاعيلن', 'مفاعيل', 'مفاعي'],
            'فاعلاتن': ['فاعلاتن', 'فاعلات', 'فاعلا'],
            'مستفعلن': ['مستفعلن', 'متفعلن', 'مستعلن'],
            'فاعلن': ['فاعلن', 'فعلن', 'فاعل'],
            'متفاعلن': ['متفاعلن', 'متفاعل', 'متفا'],
            'مفاعلتن': ['مفاعلتن', 'مفاعلتن', 'مفاعلت']
        }

        # Define meters with their possible variations
        self.meters = {
            'الطويل': [
                'فعولن مفاعيلن فعولن مفاعيلن',
                'فعولن مفاعيلن فعول مفاعيلن',
                'فعول مفاعيلن فعولن مفاعيلن',
                'فعول مفاعيلن فعول مفاعيلن'
            ],
            'البسيط': [
                'مستفعلن فاعلن مستفعلن فاعلن',
                'متفعلن فاعلن مستفعلن فاعلن',
                'مستفعلن فعلن مستفعلن فعلن'
            ],
            'الكامل': [
                'متفاعلن متفاعلن متفاعلن',
                'متفاعلن متفاعلن متفا',
                'متْفاعلن متْفاعلن متْفاعلن'
            ],
            'الوافر': [
                'مفاعلتن مفاعلتن فعولن',
                'مفاعلتن مفاعلتن فعولن',
                'مفاعلتن مفاعلتن فعول'
            ]
            # Add more meters with variations as needed
        }

        # Arabic letters and their properties
        self.arabic_letters = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.long_vowels = set('اوي')
        self.consonants = self.arabic_letters - self.long_vowels

    def clean_text(self, text: str) -> str:
        """Remove diacritics and normalize Arabic text."""
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)  # Remove diacritics
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces
        return text.strip()

    def get_syllables(self, word: str) -> List[str]:
        """
        Extract syllables from an Arabic word.
        This is a simplified version - in practice you'd need more complex rules.
        """
        syllables = []
        current_syllable = ''
        word = self.clean_text(word)
        
        i = 0
        while i < len(word):
            char = word[i]
            
            # Skip non-Arabic letters
            if char not in self.arabic_letters:
                i += 1
                continue
                
            # Start new syllable with consonant
            if char in self.consonants:
                current_syllable = char
                i += 1
                
                # Add following vowel if exists
                if i < len(word) and word[i] in self.long_vowels:
                    current_syllable += word[i]
                    i += 1
                    
                syllables.append(current_syllable)
                current_syllable = ''
            
            # Handle long vowels
            elif char in self.long_vowels:
                if current_syllable:
                    current_syllable += char
                else:
                    current_syllable = char
                syllables.append(current_syllable)
                current_syllable = ''
                i += 1
                
        return syllables

    def get_meter_pattern(self, text: str) -> str:
        """Convert text to meter pattern based on syllable analysis."""
        words = text.split()
        pattern = []
        
        for word in words:
            syllables = self.get_syllables(word)
            for syl in syllables:
                if len(syl) == 1:  # Short syllable
                    pattern.append('∪')
                else:  # Long syllable
                    pattern.append('−')
                    
        return ' '.join(pattern)

    def match_meter(self, text: str) -> List[Tuple[str, float]]:
        """
        Find matching meters for given text.
        Returns list of (meter_name, confidence) tuples.
        """
        text_pattern = self.get_meter_pattern(text)
        matches = []
        
        for meter_name, variations in self.meters.items():
            best_match_score = 0
            for variation in variations:
                meter_pattern = self.get_meter_pattern(variation)
                
                # Calculate similarity score
                score = self.calculate_similarity(text_pattern, meter_pattern)
                best_match_score = max(best_match_score, score)
            
            if best_match_score > 0.7:  # Threshold for considering it a match
                matches.append((meter_name, best_match_score))
                
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def calculate_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two meter patterns."""
        # Remove spaces for comparison
        p1 = pattern1.replace(' ', '')
        p2 = pattern2.replace(' ', '')
        
        # Dynamic programming for sequence alignment
        m, n = len(p1), len(p2)
        dp = np.zeros((m + 1, n + 1))
        
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i, j] = j
                elif j == 0:
                    dp[i, j] = i
                elif p1[i - 1] == p2[j - 1]:
                    dp[i, j] = dp[i - 1, j - 1]
                else:
                    dp[i, j] = 1 + min(dp[i - 1, j],      # deletion
                                     dp[i, j - 1],         # insertion
                                     dp[i - 1, j - 1])     # substitution
                    
        max_len = max(len(p1), len(p2))
        similarity = 1 - (dp[m, n] / max_len)
        return similarity

def main():
    st.title("Arabic Poetry Meter Analyzer محلل البحور الشعرية")
    st.write("Enter a line of Arabic poetry to identify its meter البحر الشعري")
    
    analyzer = ArabicMeterAnalyzer()
    
    # Text input for the poetry line
    poetry_line = st.text_area("Enter your poetry line here:", "")
    
    if st.button("Analyze"):
        if poetry_line:
            # Clean and analyze the text
            cleaned_text = analyzer.clean_text(poetry_line)
            pattern = analyzer.get_meter_pattern(cleaned_text)
            
            # Find matching meters
            matches = analyzer.match_meter(cleaned_text)
            
            if matches:
                st.success("Potential meters found!")
                for meter_name, confidence in matches[:3]:  # Show top 3 matches
                    st.write(f"- {meter_name} (Confidence: {confidence:.1f}%)")
                    st.write(f"  Pattern variations:")
                    for variation in analyzer.meters[meter_name]:
                        st.write(f"    {variation}")
                
                # Show the analyzed pattern for debugging
                st.write("\nDetected pattern:", pattern)
                st.write("\nSyllable breakdown:")
                for word in cleaned_text.split():
                    st.write(f"  {word}: {analyzer.get_syllables(word)}")
            else:
                st.warning("No matching meter found. Please check the text or try another line.")
        else:
            st.error("Please enter a line of poetry to analyze.")

if __name__ == "__main__":
    main()
