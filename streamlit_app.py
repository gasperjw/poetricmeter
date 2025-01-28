import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        self.consonants = set('ءابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.short_vowels = set('\u064E\u064F\u0650')  # FATHA, DAMMA, KASRA
        self.long_vowels = set('اوي')
        self.sukun = '\u0652'  # ARABIC SUKUN
        self.shadda = '\u0651'  # ARABIC SHADDA
        self.tanwin = set('\u064B\u064C\u064D')  # FATHATAN, DAMMATAN, KASRATAN

    def debug_char(self, c: str) -> str:
        """Return debug info for a character"""
        if c in self.short_vowels:
            return f"short_vowel(U+{ord(c):04X})"
        elif c == self.sukun:
            return f"sukun(U+{ord(c):04X})"
        elif c in self.long_vowels:
            return f"long_vowel({c})"
        elif c in self.consonants:
            return f"consonant({c})"
        else:
            return f"other({c}:U+{ord(c):04X})"

    def analyze_syllable(self, chars: list, start: int) -> Tuple[int, Tuple[str, str, str]]:
        """Analyze a single syllable starting at position start"""
        i = start
        debug_info = []
        
        # Must start with consonant
        if chars[i] not in self.consonants:
            return i + 1, None
            
        consonant = chars[i]
        debug_info.append(f"Found consonant: {consonant}")
        i += 1
        
        # Must have short vowel
        if i >= len(chars) or chars[i] not in self.short_vowels:
            return i, None
            
        vowel = chars[i]
        debug_info.append(f"Found vowel: {vowel}")
        i += 1
        
        # Look ahead for syllable closure
        syllable_type = 'V'  # Default to open syllable
        end_char = ''
        
        if i < len(chars):
            if chars[i] == self.sukun:
                debug_info.append(f"Found sukun")
                syllable_type = 'S'
                end_char = chars[i]
                i += 1
            elif chars[i] in self.long_vowels:
                debug_info.append(f"Found long vowel: {chars[i]}")
                syllable_type = 'S'
                end_char = chars[i]
                i += 1
            elif chars[i] in self.tanwin:
                debug_info.append(f"Found tanwin: {chars[i]}")
                syllable_type = 'S'
                end_char = chars[i]
                i += 1
            elif chars[i] in self.consonants and i+1 < len(chars) and chars[i+1] == self.sukun:
                debug_info.append(f"Found consonant+sukun: {chars[i]}{chars[i+1]}")
                syllable_type = 'S'
                end_char = chars[i] + chars[i+1]
                i += 2
        
        syllable_text = consonant + vowel + end_char
        return i, (syllable_text, syllable_type, ' | '.join(debug_info))

    def get_syllables(self, text: str) -> List[Tuple[str, str, str]]:
        """Break text into syllables with detailed debugging"""
        syllables = []
        chars = list(text)
        i = 0
        
        st.write("### Character by character analysis:")
        while i < len(chars):
            st.write(f"Position {i}: {self.debug_char(chars[i])}")
            
            if chars[i] == ' ':
                i += 1
                continue
                
            new_i, syllable = self.analyze_syllable(chars, i)
            if syllable:
                syllables.append(syllable)
            i = new_i
            
        return syllables

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    text = st.text_input(
        "Enter Arabic poetry line:",
        value="قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِي"
    )
    
    if st.button("Analyze"):
        analyzer = ArabicMeterAnalyzer()
        
        st.write("### Initial text analysis")
        st.write("Text length:", len(text))
        st.write("Characters:", [f"{c}(U+{ord(c):04X})" for c in text])
        
        syllables = analyzer.get_syllables(text)
        
        st.write("### Syllable Analysis")
        for syl, pat, debug in syllables:
            st.write(f"\nSyllable: {syl}")
            st.write(f"Pattern: {pat}")
            st.write(f"Debug: {debug}")
        
        pattern = ''.join(p for _, p, _ in syllables)
        feet = [pattern[i:i+4] for i in range(0, len(pattern), 4)]
        
        st.write("\n### Final Pattern")
        st.write("Detected:", ' '.join(feet))
        st.write("Expected:", "VSVS VVSVS VSVS VVSVS")

if __name__ == "__main__":
    main()
