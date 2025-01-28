import streamlit as st
import re
from typing import List, Tuple, Dict

class ArabicSyllableAnalyzer:
    def __init__(self):
        # Essential Arabic character sets
        self.consonants = set('ءابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.long_vowels = set('اوي')
        self.short_vowels = set('َُِ')  # Fatha, Damma, Kasra
        self.tanwin = set('ًٌٍ')  # Tanwin forms
        self.sukun = 'ْ'
        self.shadda = 'ّ'
        
        # Meters with their patterns
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
        
    def analyze_syllables(self, text: str) -> List[Dict]:
        """
        Analyze text into syllables with detailed debugging information.
        Returns list of syllables with their properties.
        """
        syllables = []
        i = 0
        debug_info = []
        
        while i < len(text):
            if not text[i] in self.consonants:
                i += 1
                continue
                
            # Start of potential syllable
            syllable_start = i
            consonant = text[i]
            i += 1
            
            # Look for vowel marks
            vowel_mark = ''
            if i < len(text) and text[i] in self.short_vowels:
                vowel_mark = text[i]
                i += 1
            
            # Look ahead for potential syllable endings
            syllable_type = ''
            next_char = text[i] if i < len(text) else ''
            
            if vowel_mark:  # We have a valid syllable start (CV)
                if next_char in self.long_vowels:  # CVV
                    syllable_type = 'S'  # ساكن
                    i += 1
                elif next_char == self.sukun:  # CVC
                    syllable_type = 'S'  # ساكن
                    i += 1
                elif next_char == self.shadda:  # CVCC
                    syllable_type = 'S'  # ساكن
                    i += 1
                else:  # CV
                    syllable_type = 'V'  # متحرك
                
                syllable_info = {
                    'text': text[syllable_start:i],
                    'type': syllable_type,
                    'consonant': consonant,
                    'vowel_mark': vowel_mark,
                    'ending': next_char if syllable_type == 'S' else ''
                }
                syllables.append(syllable_info)
                debug_info.append(f"{syllable_info['text']}({syllable_info['type']})")
            
        return syllables, debug_info

    def get_pattern(self, text: str) -> Tuple[str, List[str]]:
        """Get meter pattern from text with debugging info."""
        syllables, debug_info = self.analyze_syllables(text)
        pattern = ''.join(s['type'] for s in syllables)
        
        # Insert spaces to group into feet
        segmented_pattern = ''
        for i, char in enumerate(pattern):
            segmented_pattern += char
            if (i + 1) % 4 == 0 and i < len(pattern) - 1:
                segmented_pattern += ' '
                
        return segmented_pattern, debug_info

    def find_meter(self, pattern: str) -> List[Tuple[str, float]]:
        """Find matching meters for pattern."""
        matches = []
        pattern_no_spaces = pattern.replace(' ', '')
        
        for meter, meter_pattern in self.meters.items():
            meter_no_spaces = meter_pattern.replace(' ', '')
            if len(pattern_no_spaces) > len(meter_no_spaces) * 0.5:  # Only check if lengths are somewhat similar
                similarity = self.calculate_similarity(pattern_no_spaces, meter_no_spaces)
                if similarity > 0.8:
                    matches.append((meter, similarity))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def calculate_similarity(self, p1: str, p2: str) -> float:
        """Calculate similarity between two patterns."""
        max_len = max(len(p1), len(p2))
        min_len = min(len(p1), len(p2))
        matches = sum(1 for i in range(min_len) if p1[i] == p2[i])
        return matches / max_len

def main():
    st.title("Arabic Meter Analyzer محلل البحور الشعرية")
    
    st.markdown("""
    ### Input Requirements متطلبات الإدخال
    - Full diacritical marks (تشكيل كامل)
    - Enter a single line
    - Include all harakat (حركات)
    """)
    
    # Text input
    text = st.text_input(
        "Enter Arabic poetry line:",
        value="قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِلِ"
    )
    
    analyzer = ArabicSyllableAnalyzer()
    
    if st.button("Analyze"):
        if not text:
            st.error("Please enter text")
            return
            
        # Get pattern with debugging info
        pattern, debug_info = analyzer.get_pattern(text)
        
        # Show detailed analysis
        st.subheader("Detailed Analysis التحليل المفصل")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Syllable Breakdown تقطيع المقاطع**")
            for syllable in debug_info:
                st.write(syllable)
                
        with col2:
            st.write("**Detected Pattern النمط المكتشف**")
            st.write(pattern)
        
        # Find matching meters
        matches = analyzer.find_meter(pattern)
        
        if matches:
            st.success("Matching Meters البحور المطابقة")
            for meter, confidence in matches:
                st.write(f"- {meter} ({confidence*100:.1f}%)")
                st.write(f"  Expected: {analyzer.meters[meter]}")
                st.write(f"  Detected: {pattern}")
        else:
            st.warning("No matching meter found")
            st.write("Detected pattern:", pattern)

if __name__ == "__main__":
    main()
