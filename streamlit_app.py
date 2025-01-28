import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        # Character sets
        self.consonants = set('ءابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.short_vowels = set('َُِ')      # Fatha, Damma, Kasra
        self.long_vowels = set('اوي')       # Alif, Waw, Ya
        self.sukun = 'ْ'
        self.shadda = 'ّ'
        self.tanwin = set('ًٌٍ')
        
    def get_syllables(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Break text into syllables, following Arabic prosody rules strictly.
        Each syllable must start with a consonant + vowel.
        """
        syllables = []
        chars = list(text)  # Convert to list for easier handling
        i = 0
        
        while i < len(chars):
            # Skip non-consonants at start
            if chars[i] not in self.consonants:
                i += 1
                continue
            
            start = i
            consonant = chars[i]
            i += 1
            
            # Look for vowel
            if i < len(chars) and chars[i] in self.short_vowels:
                vowel = chars[i]
                i += 1
                
                # Now check what closes the syllable
                if i < len(chars):
                    if chars[i] in self.long_vowels:  # CVV like فا
                        syllables.append((
                            ''.join(chars[start:i+1]),
                            'S',
                            f'CVV: {consonant}{vowel}{chars[i]}'
                        ))
                        i += 1
                    elif chars[i] == self.sukun:  # CVC like مِنْ
                        syllables.append((
                            ''.join(chars[start:i+1]),
                            'S',
                            f'CVC: {consonant}{vowel}{self.sukun}'
                        ))
                        i += 1
                    elif chars[i] in self.tanwin:  # CVN like بٍ
                        syllables.append((
                            ''.join(chars[start:i+1]),
                            'S',
                            f'CVN: {consonant}{vowel}{chars[i]}'
                        ))
                        i += 1
                    elif chars[i] == self.shadda:  # CVCC like شَدّ
                        syllables.append((
                            ''.join(chars[start:i+1]),
                            'S',
                            f'CVCC: {consonant}{vowel}{self.shadda}'
                        ))
                        i += 1
                    else:  # CV like بِ
                        syllables.append((
                            ''.join(chars[start:i]),
                            'V',
                            f'CV: {consonant}{vowel}'
                        ))
                else:  # End of text
                    syllables.append((
                        ''.join(chars[start:i]),
                        'V',
                        f'CV: {consonant}{vowel}'
                    ))
                    
        return syllables

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    example = "قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِ"
    
    st.markdown(f"""
    ### Instructions التعليمات
    Each syllable must include:
    - Consonant (حرف صحيح)
    - Short vowel (حركة: َُِ)
    - Optional ending: long vowel (ا و ي) / sukun (ْ) / tanwin (ًٌٍ)
    
    Test line:
    {example}
    """)
    
    # Text input
    text = st.text_input(
        "Enter Arabic poetry line:",
        value=example
    )
    
    analyzer = ArabicMeterAnalyzer()
    
    if st.button("Analyze"):
        if not text:
            st.error("Please enter text")
            return
        
        # Analyze syllables
        syllables = analyzer.get_syllables(text)
        
        # Show analysis in table
        st.markdown("### Syllable Analysis تحليل المقاطع")
        st.markdown("| Syllable | Pattern | Type |")
        st.markdown("|----------|---------|------|")
        for syl, pat, reason in syllables:
            st.markdown(f"| {syl} | {pat} | {reason} |")
        
        # Show pattern
        pattern = ''.join(p for _, p, _ in syllables)
        
        # Group into feet (every 2 syllables for taf'ilat)
        feet = []
        for i in range(0, len(pattern), 4):
            feet.append(pattern[i:i+4])
        segmented_pattern = ' '.join(feet)
        
        st.markdown("### Detected Pattern النمط المكتشف")
        st.write(segmented_pattern)
        
        # Compare with expected
        st.markdown("### Expected Pattern (الطويل)")
        st.write("VSVS VVSVS VSVS VVSVS")
        
        # Detailed breakdown
        st.markdown("### Foot Analysis تحليل التفعيلات")
        for i, foot in enumerate(feet, 1):
            st.write(f"Foot {i}: {foot}")

if __name__ == "__main__":
    main()
