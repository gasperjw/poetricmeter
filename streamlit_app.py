import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        self.consonants = set('ءابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.short_vowels = set('َُِ')
        self.long_vowels = set('اوي')
        self.sukun = 'ْ'
        self.shadda = 'ّ'
        self.tanwin = set('ًٌٍ')

    def get_syllables(self, text: str) -> List[Tuple[str, str, str]]:
        """Break text into syllables using strict Arabic prosody rules."""
        syllables = []
        chars = list(text)
        i = 0
        
        while i < len(chars):
            # Skip non-letters
            if chars[i] not in self.consonants and chars[i] != ' ':
                i += 1
                continue
                
            # Skip spaces but note word boundary
            if chars[i] == ' ':
                i += 1
                continue
            
            start = i
            # Find next consonant + vowel sequence
            if chars[i] in self.consonants:
                consonant = chars[i]
                i += 1
                
                # Look for vowel
                if i < len(chars) and chars[i] in self.short_vowels:
                    vowel = chars[i]
                    i += 1
                    
                    # Look ahead for syllable end
                    is_closed = False
                    if i < len(chars):
                        # Case 1: Closed by sukun
                        if chars[i] == self.sukun:
                            syllables.append((
                                ''.join(chars[start:i+1]),
                                'S',
                                f'CVC (sukun): {consonant}{vowel}ْ'
                            ))
                            is_closed = True
                            i += 1
                        
                        # Case 2: Closed by long vowel
                        elif chars[i] in self.long_vowels:
                            syllables.append((
                                ''.join(chars[start:i+1]),
                                'S',
                                f'CVV: {consonant}{vowel}{chars[i]}'
                            ))
                            is_closed = True
                            i += 1
                            
                        # Case 3: Closed by tanwin
                        elif chars[i] in self.tanwin:
                            syllables.append((
                                ''.join(chars[start:i+1]),
                                'S',
                                f'CVN: {consonant}{vowel}{chars[i]}'
                            ))
                            is_closed = True
                            i += 1
                            
                        # Case 4: Next char is consonant + sukun
                        elif (i+1 < len(chars) and chars[i] in self.consonants 
                              and i+2 < len(chars) and chars[i+2] == self.sukun):
                            syllables.append((
                                ''.join(chars[start:i+2]),
                                'S',
                                f'CVCC: {consonant}{vowel}{chars[i]}ْ'
                            ))
                            is_closed = True
                            i += 2
                    
                    # Open syllable if not closed
                    if not is_closed:
                        syllables.append((
                            ''.join(chars[start:i]),
                            'V',
                            f'CV: {consonant}{vowel}'
                        ))
                
        return syllables

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    st.markdown("""
    ### Test with:
    قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِي
    
    Make sure to mark:
    - All short vowels (حركات: َُِ)
    - All sukun (سكون: ْ)
    - Word boundaries (spaces)
    """)
    
    text = st.text_input(
        "Enter Arabic poetry line:",
        value="قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِي"
    )
    
    if st.button("Analyze"):
        if not text:
            st.error("Please enter text")
            return
            
        analyzer = ArabicMeterAnalyzer()
        syllables = analyzer.get_syllables(text)
        
        # Display analysis
        st.markdown("### Syllable Analysis تحليل المقاطع")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Raw syllables:")
            for syl, pat, reason in syllables:
                st.write(f"{syl} ({pat})")
        
        with col2:
            st.markdown("#### Pattern details:")
            for syl, pat, reason in syllables:
                st.write(f"{reason}")
        
        # Generate pattern
        pattern = ''.join(p for _, p, _ in syllables)
        feet = [pattern[i:i+4] for i in range(0, len(pattern), 4)]
        
        st.markdown("### Complete Pattern Analysis")
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("#### Detected:")
            st.write(' '.join(feet))
            
        with col4:
            st.markdown("#### Expected (الطويل):")
            st.write("VSVS VVSVS VSVS VVSVS")

if __name__ == "__main__":
    main()
