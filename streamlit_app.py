import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        self.consonants = set('ءابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.short_vowels = set('\u064E\u064F\u0650')  # FATHA, DAMMA, KASRA
        self.long_vowels = set('ا')  # Only Alif is always a long vowel; و and ي are context-dependent
        self.sukun = '\u0652'  # ARABIC SUKUN
        self.shadda = '\u0651'  # ARABIC SHADDA
        self.tanwin = set('\u064B\u064C\u064D')  # FATHATAN, DAMMATAN, KASRATAN
        self.tanwin_to_vowel = {
            '\u064B': '\u064E',  # Fathatan → FATHA
            '\u064C': '\u064F',  # Dammatan → DAMMA
            '\u064D': '\u0650'   # Kasratan → KASRA
        }

    def debug_char(self, c: str) -> str:
        """Return debug info for a character"""
        if c in self.consonants:
            return f"consonant({c})"
        elif c in self.short_vowels:
            return f"short_vowel(U+{ord(c):04X})"
        elif c == self.sukun:
            return f"sukun(U+{ord(c):04X})"
        elif c in self.long_vowels:
            return f"long_vowel({c})"
        elif c in self.tanwin:
            return f"tanwin({c})"
        else:
            return f"other({c}:U+{ord(c):04X})"

    def analyze_syllable(self, chars: list, start: int) -> Tuple[int, Tuple[str, str, str]]:
        """Analyze a single syllable starting at position start"""
        i = start
        debug_info = []
        
        # Skip non-consonant starters
        if i >= len(chars) or chars[i] not in self.consonants:
            return i + 1, None
            
        consonant = chars[i]
        debug_info.append(f"Found consonant: {consonant}")
        i += 1
        
        # Check for vowel (short vowel or tanwin)
        if i >= len(chars):
            return i, None
            
        current_char = chars[i]
        vowel = None
        
        # Handle short vowels
        if current_char in self.short_vowels:
            vowel = current_char
            debug_info.append(f"Found short vowel: {vowel}")
            i += 1
        # Handle tanwin as vowels
        elif current_char in self.tanwin:
            vowel = self.tanwin_to_vowel.get(current_char)
            if not vowel:
                return i, None
            debug_info.append(f"Found tanwin {current_char} mapped to vowel {vowel}")
            i += 1
        else:
            return i, None  # No valid vowel found
        
        # Determine syllable closure
        syllable_type = 'V'  # Open syllable by default
        end_chars = []
        
        # Check for closing characters
        while i < len(chars):
            # Check for sukun
            if chars[i] == self.sukun:
                debug_info.append(f"Found sukun at {i}")
                end_chars.append(chars[i])
                syllable_type = 'S'
                i += 1
            # Check for long vowels (only Alif in this set)
            elif chars[i] in self.long_vowels:
                debug_info.append(f"Found long vowel {chars[i]} at {i}")
                end_chars.append(chars[i])
                syllable_type = 'S'
                i += 1
            # Check for consonant with sukun
            elif i+1 < len(chars) and chars[i] in self.consonants and chars[i+1] == self.sukun:
                debug_info.append(f"Found consonant {chars[i]} with sukun at {i}")
                end_chars.extend(chars[i:i+2])
                syllable_type = 'S'
                i += 2
            # Check for tanwin (already handled as vowels)
            else:
                break
                
        # Handle special case where tanwin implies closure
        if current_char in self.tanwin:
            debug_info.append("Tanwin implies syllable closure")
            syllable_type = 'S'
            end_chars.append(current_char)
        
        syllable_text = consonant + (vowel if vowel else '') + ''.join(end_chars)
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
                st.write(f"Formed syllable: {syllable}")
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
        # Improved foot division based on known meter patterns
        feet = []
        current_foot = []
        for p in pattern:
            current_foot.append(p)
            if p == 'S' and len(current_foot) in [2, 4, 5]:
                feet.append(''.join(current_foot))
                current_foot = []
        if current_foot:
            feet.append(''.join(current_foot))
        
        st.write("\n### Final Pattern")
        st.write("Detected:", ' '.join(feet))
        st.write("Expected:", "VSVS VVSVS VSVS VVSVS")

if __name__ == "__main__":
    main()
