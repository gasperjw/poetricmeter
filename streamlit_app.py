import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        # Define the basic meters with their exact patterns
        self.meters = {
            'الطويل': 'فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ',
            'المديد': 'فَاعِلَاتُنْ فَاعِلُنْ فَاعِلَاتُنْ',
            'البسيط': 'مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ',
            'الوافر': 'مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ',
            'الكامل': 'مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ',
            'الهزج': 'مَفَاعِيلُنْ مَفَاعِيلُنْ',
            'الرجز': 'مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ',
            'الرمل': 'فَاعِلَاتُنْ فَاعِلَاتُنْ فَاعِلَاتُنْ'
        }
        
        # Diacritical marks we expect (excluding sukun)
        self.diacritics = 'ًٌٍَُِّْ'
        
    def clean_line(self, text: str) -> str:
        """Clean the input line and ensure it's properly formatted."""
        # Remove any existing sukun marks
        text = re.sub('ْ', '', text)
        
        # Remove multiple spaces and trim
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into words and join with single space
        return ' '.join(text.split())

    def extract_pattern(self, text: str) -> str:
        """Convert text to CV pattern (consonant-vowel pattern)."""
        pattern = ''
        prev_char = ''
        
        for char in text:
            if char in self.diacritics:
                if char in 'َُِ':  # Short vowels
                    pattern += 'v'
                elif char in 'ًٌٍّ':  # Double marks or shadda
                    pattern += 'vv'
            elif re.match('[ا-ي]', char):  # Arabic letters
                if prev_char not in self.diacritics:
                    pattern += 'c'
            prev_char = char
            
        return pattern

    def match_meter(self, pattern: str) -> List[Tuple[str, float]]:
        """Find matching meters based on CV pattern."""
        matches = []
        
        for meter_name, meter_text in self.meters.items():
            meter_pattern = self.extract_pattern(meter_text)
            similarity = self.calculate_similarity(pattern, meter_pattern)
            if similarity > 0.85:  # Higher threshold for more accuracy
                matches.append((meter_name, similarity))
                
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def calculate_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two patterns."""
        if not pattern1 or not pattern2:
            return 0.0
            
        # Dynamic programming approach for sequence alignment
        m, n = len(pattern1), len(pattern2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if pattern1[i-1] == pattern2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j],      # deletion
                                     dp[i][j-1],         # insertion
                                     dp[i][j-1])         # substitution
                                     
        max_len = max(m, n)
        return 1 - (dp[m][n] / max_len)

def main():
    st.title("Arabic Poetry Meter Analyzer محلل البحور الشعرية")
    st.markdown("""
    ### Instructions التعليمات
    1. Enter a **single line** of Arabic poetry
    2. Make sure all diacritical marks are present (except sukun)
    3. The line should be fully vowelized (مُشَكّل)
    """)
    
    # Text input with clear placeholder showing required format
    placeholder_text = "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ"
    poetry_line = st.text_input(
        "Enter your poetry line here:", 
        placeholder=placeholder_text
    )
    
    # Prevent multi-line input
    if '\n' in poetry_line:
        st.error("Please enter only one line of poetry")
        return
        
    analyzer = ArabicMeterAnalyzer()
    
    if st.button("Analyze التحليل"):
        if poetry_line:
            # Clean and process the line
            cleaned_line = analyzer.clean_line(poetry_line)
            pattern = analyzer.extract_pattern(cleaned_line)
            
            # Find matches
            matches = analyzer.match_meter(pattern)
            
            if matches:
                st.success("Meter identified! البحر المحدد")
                for meter_name, confidence in matches[:2]:  # Show top 2 matches
                    st.write(f"- {meter_name} ({confidence*100:.1f}%)")
                    st.write(f"  Original pattern: {analyzer.meters[meter_name]}")
                
                # Debug information in expander
                with st.expander("Show technical details"):
                    st.write("Extracted pattern:", pattern)
                    st.write("Cleaned text:", cleaned_line)
            else:
                st.warning("No matching meter found. Please check the vowelization.")
        else:
            st.error("Please enter a line of poetry")

if __name__ == "__main__":
    main()
