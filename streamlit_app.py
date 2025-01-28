import streamlit as st
import re
from typing import List, Tuple

class ArabicMeterAnalyzer:
    def __init__(self):
        # Character sets
        self.short_vowels = set('َُِ')      # Fatha, Damma, Kasra
        self.long_vowels = set('اوي')       # Alif, Waw, Ya
        self.sukun = 'ْ'
        self.shadda = 'ّ'
        self.tanwin = set('ًٌٍ')
        
    def get_syllables(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Break text into syllables, returning each with its pattern and reason.
        Returns: List of (syllable_text, pattern, reason)
        """
        syllables = []
        text = ' '.join(text.split())  # Normalize spaces
        i = 0
        
        while i < len(text):
            # Skip spaces
            if text[i].isspace():
                i += 1
                continue
                
            # Find next short vowel
            vowel_pos = -1
            for j in range(i+1, min(i+4, len(text))):
                if text[j] in self.short_vowels:
                    vowel_pos = j
                    break
            
            if vowel_pos == -1:  # No vowel found
                i += 1
                continue
                
            # Look at what follows the vowel
            next_pos = vowel_pos + 1
            if next_pos < len(text):
                if text[next_pos] in self.long_vowels:  # CVV
                    syllables.append((
                        text[i:next_pos+1],
                        'S',
                        f'Closed by long vowel {text[next_pos]}'
                    ))
                    i = next_pos + 1
                elif text[next_pos] == self.sukun:  # CVC
                    syllables.append((
                        text[i:next_pos+1],
                        'S',
                        'Closed by sukun'
                    ))
                    i = next_pos + 1
                elif text[next_pos] == self.shadda:  # CVCC
                    syllables.append((
                        text[i:next_pos+1],
                        'S',
                        'Closed by shadda'
                    ))
                    i = next_pos + 1
                elif text[next_pos] in self.tanwin:  # CV + tanwin
                    syllables.append((
                        text[i:next_pos+1],
                        'S',
                        'Closed by tanwin'
                    ))
                    i = next_pos + 1
                else:  # CV
                    syllables.append((
                        text[i:vowel_pos+1],
                        'V',
                        'Open syllable'
                    ))
                    i = vowel_pos + 1
            else:  # End of text, must be CV
                syllables.append((
                    text[i:vowel_pos+1],
                    'V',
                    'Open syllable at end'
                ))
                i = vowel_pos + 1
                
        return syllables

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    # Example text
    example = "قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيْبٍ وَمَنْزِلِ"
    
    st.markdown(f"""
    ### Test with this line:
    {example}
    
    Make sure all marks are included:
    - Short vowels (فتحة/ضمة/كسرة): َ ُ ِ
    - Sukun: ْ
    - Long vowels (حروف المد): ا و ي
    - Tanwin: ً ٌ ٍ
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
        
        # Show detailed analysis
        st.subheader("Syllable Analysis تحليل المقاطع")
        
        # Display syllables in a table
        st.write("| Syllable | Pattern | Reason |")
        st.write("|----------|---------|---------|")
        for syl, pat, reason in syllables:
            st.write(f"| {syl} | {pat} | {reason} |")
        
        # Show final pattern
        pattern = ''.join(p for _, p, _ in syllables)
        segmented_pattern = ' '.join(pattern[i:i+4] for i in range(0, len(pattern), 4))
        
        st.subheader("Detected Pattern النمط المكتشف")
        st.write(segmented_pattern)
        
        st.subheader("Expected Pattern (الطويل)")
        st.write("VSVS VVSVS VSVS VVSVS")

if __name__ == "__main__":
    main()
