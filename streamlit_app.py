import streamlit as st
import re
from typing import List, Tuple, Dict

class ArabicSyllableAnalyzer:
    def __init__(self):
        # Define character sets
        self.consonants = set('ءابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.long_vowels = set('اوي')
        self.short_vowels = 'َُِ'  # Fatha, Damma, Kasra
        self.sukun = 'ْ'
        self.shadda = 'ّ'
        self.tanwin = 'ًٌٍ'
        
        # Meters with their patterns
        self.meters = {
            'الطويل': 'VSVS VVSVS VSVS VVSVS'
        }

    def analyze_syllables(self, text: str) -> List[Dict]:
        """Analyze text into syllables with detailed tracking."""
        result = []
        i = 0
        debug = []
        
        while i < len(text):
            if text[i] not in self.consonants:
                i += 1
                continue
                
            # Start of syllable
            start = i
            syllable = {'text': '', 'type': '', 'debug': ''}
            consonant = text[i]
            i += 1
            
            # Look for vowel
            if i < len(text) and text[i] in self.short_vowels:
                vowel = text[i]
                i += 1
                
                # Look ahead for syllable closure
                if i < len(text):
                    if text[i] in self.long_vowels:  # CVV
                        syllable['type'] = 'S'
                        syllable['text'] = text[start:i+1]
                        syllable['debug'] = f"CVV: {consonant}+{vowel}+{text[i]}"
                        i += 1
                    elif text[i] == self.sukun:  # CVC
                        syllable['type'] = 'S'
                        syllable['text'] = text[start:i+1]
                        syllable['debug'] = f"CVC: {consonant}+{vowel}+sukun"
                        i += 1
                    elif text[i] == self.shadda:  # CVCC
                        syllable['type'] = 'S'
                        syllable['text'] = text[start:i+1]
                        syllable['debug'] = f"CVCC: {consonant}+{vowel}+shadda"
                        i += 1
                    else:  # CV
                        syllable['type'] = 'V'
                        syllable['text'] = text[start:i]
                        syllable['debug'] = f"CV: {consonant}+{vowel}"
                
                if syllable['type']:  # Valid syllable found
                    result.append(syllable)
                    debug.append(f"{syllable['text']}({syllable['type']}-{syllable['debug']})")
            
        return result, debug

    def get_pattern(self, text: str) -> Tuple[str, List[str]]:
        """Convert text to meter pattern with debugging info."""
        syllables, debug = self.analyze_syllables(text)
        
        # Build pattern with proper spacing between feet
        pattern = ''
        for i, syl in enumerate(syllables):
            pattern += syl['type']
            # Add space every 4 syllables
            if (i + 1) % 4 == 0 and i < len(syllables) - 1:
                pattern += ' '
        
        return pattern, debug

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    st.markdown("""
    ### Test with: قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِ
    Make sure to include all diacritical marks:
    - Short vowels (فتحة/ضمة/كسرة): َ ُ ِ
    - Sukun: ْ
    - Long vowels (حروف المد): ا و ي
    """)
    
    # Text input
    text = st.text_input(
        "Enter Arabic poetry line:",
        value="قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِ"
    )
    
    analyzer = ArabicSyllableAnalyzer()
    
    if st.button("Analyze"):
        if not text:
            st.error("Please enter text")
            return
            
        # Get pattern with debugging
        pattern, debug_info = analyzer.get_pattern(text)
        
        # Show detailed analysis
        st.subheader("Syllable Analysis تحليل المقاطع")
        for d in debug_info:
            st.write(d)
            
        st.subheader("Detected Pattern النمط المكتشف")
        st.write(pattern)
        
        st.subheader("Expected Pattern for الطويل")
        st.write("VSVS VVSVS VSVS VVSVS")

if __name__ == "__main__":
    main()
