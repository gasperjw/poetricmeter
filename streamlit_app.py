import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        self.meters = {
            'الطويل': 'VSVS VVSVS VSVS VVSVS',
            'المديد': 'VSVVS VSV VSVVS',
            'البسيط': 'VSSVS VSV VSSVS VSV',
            'الوافر': 'VVSVS VVSVS VSV',
            'الكامل': 'VVVVS VVVVS VVVVS',
            'الهزج': 'VVSVS VVSVS',
            'الرجز': 'VSSVS VSSVS VSSVS',
            'الرمل': 'VSVVS VSVVS VSVVS'
        }
        
        # Define Arabic characters and diacritics
        self.short_vowels = 'َُِ'  # فتحة ضمة كسرة
        self.long_vowels = 'اوي'   # ا و ي
        self.sukun = 'ْ'
        self.shadda = 'ّ'
        
    def get_pattern(self, text: str) -> str:
        """Convert Arabic text to meter pattern."""
        pattern = ''
        i = 0
        text = ' '.join(text.split())  # Normalize spaces
        
        while i < len(text):
            if text[i] == ' ':
                if pattern and pattern[-1] != ' ':
                    pattern += ' '
                i += 1
                continue
                
            # Skip if not Arabic letter
            if not re.match('[ء-ي]', text[i]):
                i += 1
                continue
                
            # Look ahead for vowel marks
            next_char = text[i + 1] if i + 1 < len(text) else ''
            next_next_char = text[i + 2] if i + 2 < len(text) else ''
            
            # Case 1: CV (short syllable)
            if next_char in self.short_vowels:
                if (next_next_char not in self.long_vowels and 
                    next_next_char != self.sukun and 
                    next_next_char != self.shadda):
                    pattern += 'V'
                    i += 2
                    continue
            
            # Case 2: CVV (long syllable with long vowel)
            if (next_char in self.short_vowels and 
                next_next_char in self.long_vowels):
                pattern += 'S'
                i += 3
                continue
            
            # Case 3: CVC (long syllable with sukun)
            if (next_char in self.short_vowels and 
                next_next_char == self.sukun):
                pattern += 'S'
                i += 3
                continue
                
            # Case 4: CVCC (long syllable with shadda)
            if (next_char in self.short_vowels and 
                next_next_char == self.shadda):
                pattern += 'S'
                i += 3
                continue
                
            # Move to next character if no pattern matched
            i += 1
            
        return pattern.strip()

    def find_meter(self, pattern: str) -> List[Tuple[str, float]]:
        """Find matching meters for a pattern."""
        matches = []
        for meter, meter_pattern in self.meters.items():
            # Calculate similarity
            similarity = self.pattern_similarity(pattern, meter_pattern)
            if similarity > 0.9:  # High threshold for confidence
                matches.append((meter, similarity))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def pattern_similarity(self, p1: str, p2: str) -> float:
        """Calculate similarity between two patterns."""
        # Remove spaces for comparison
        p1 = p1.replace(' ', '')
        p2 = p2.replace(' ', '')
        
        if not p1 or not p2:
            return 0.0
            
        # Use length ratio as part of similarity
        len_ratio = min(len(p1), len(p2)) / max(len(p1), len(p2))
        
        # Count matching characters
        matches = sum(1 for i in range(min(len(p1), len(p2))) if p1[i] == p2[i])
        match_ratio = matches / max(len(p1), len(p2))
        
        return (len_ratio + match_ratio) / 2

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    st.markdown("""
    ### Instructions التعليمات
    1. Enter a single line of Arabic poetry with diacritical marks
    2. The line should include:
       - Short vowels (حركات): َ ُ ِ
       - Shadda (شدّة): ّ
       - Sukun (سكون): ْ
    """)
    
    # Example button
    if st.button("Show example"):
        st.code("قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِلِ")
    
    # Text input
    text = st.text_input(
        "Enter Arabic poetry line:",
        placeholder="أَدْخِل بَيْتَ الشِّعْرِ هُنَا"
    )
    
    analyzer = ArabicMeterAnalyzer()
    
    if st.button("Analyze"):
        if not text:
            st.error("Please enter text")
            return
            
        # Get pattern
        pattern = analyzer.get_pattern(text)
        matches = analyzer.find_meter(pattern)
        
        if matches:
            st.success("Found potential meter(s):")
            for meter, confidence in matches:
                st.write(f"- {meter} ({confidence*100:.1f}%)")
                st.write(f"  Expected pattern: {analyzer.meters[meter]}")
                
            # Show technical details
            with st.expander("Show analysis details"):
                st.write("Detected pattern:", pattern)
                st.write("Pattern explanation:")
                st.write("V = متحرك (short syllable)")
                st.write("S = ساكن (long syllable)")
        else:
            st.warning("No matching meter found. Please check the text and diacritical marks.")
            st.write("Detected pattern:", pattern)

if __name__ == "__main__":
    main()
