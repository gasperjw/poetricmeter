import streamlit as st
import re
from typing import List, Dict, Tuple

# Arabic meters with their patterns
METERS = {
    'الطويل': 'فعولن مفاعيلن فعولن مفاعيلن',
    'المديد': 'فاعلاتن فاعلن فاعلاتن',
    'البسيط': 'مستفعلن فاعلن مستفعلن فاعلن',
    'الوافر': 'مفاعلتن مفاعلتن فعولن',
    'الكامل': 'متفاعلن متفاعلن متفاعلن',
    'الهزج': 'مفاعيلن مفاعيلن',
    'الرجز': 'مستفعلن مستفعلن مستفعلن',
    'الرمل': 'فاعلاتن فاعلاتن فاعلاتن',
    'السريع': 'مستفعلن مستفعلن فاعلن',
    'المنسرح': 'مستفعلن مفعولات مستفعلن',
    'الخفيف': 'فاعلاتن مستفعلن فاعلاتن',
    'المضارع': 'مفاعيلن فاعلاتن',
    'المقتضب': 'مفعولات مستفعلن',
    'المجتث': 'مستفعلن فاعلاتن',
    'المتقارب': 'فعولن فعولن فعولن فعولن',
    'المتدارك': 'فاعلن فاعلن فاعلن فاعلن'
}

def is_arabic_letter(char: str) -> bool:
    """Check if a character is an Arabic letter."""
    return '\u0600' <= char <= '\u06FF'

def get_syllable_pattern(text: str) -> str:
    """
    Convert Arabic text to a pattern of moving (متحرك) and still (ساكن) syllables.
    Returns a string where 'v' represents متحرك and 's' represents ساكن.
    """
    pattern = ''
    i = 0
    while i < len(text):
        if not is_arabic_letter(text[i]):
            i += 1
            continue
            
        # Skip diacritics
        while i + 1 < len(text) and not is_arabic_letter(text[i + 1]):
            i += 1
            
        if i + 1 < len(text) and is_arabic_letter(text[i + 1]):
            pattern += 'v'  # متحرك
        else:
            pattern += 's'  # ساكن
        i += 1
    return pattern

def convert_meter_to_pattern(meter: str) -> str:
    """Convert a meter's taf'ilat to a syllable pattern."""
    # Mapping of basic taf'ilat to their syllable patterns
    TAFILAT_PATTERNS = {
        'فعولن': 'vvs',
        'مفاعيلن': 'vvsvs',
        'فاعلاتن': 'vsvvs',
        'فاعلن': 'vsvs',
        'مستفعلن': 'ssvvs',
        'مفاعلتن': 'vvsvs',
        'متفاعلن': 'vvvvs',
        'مفعولات': 'ssvvs'
    }
    
    pattern = ''
    for taf3ila in meter.split():
        if taf3ila in TAFILAT_PATTERNS:
            pattern += TAFILAT_PATTERNS[taf3ila]
    return pattern

def find_matching_meter(text_pattern: str) -> List[Tuple[str, float]]:
    """
    Find the matching meter for a given syllable pattern.
    Returns a list of tuples containing (meter_name, similarity_score).
    """
    matches = []
    
    for meter_name, meter_pattern in METERS.items():
        meter_syllable_pattern = convert_meter_to_pattern(meter_pattern)
        
        # Calculate similarity score
        min_len = min(len(text_pattern), len(meter_syllable_pattern))
        matching_chars = sum(1 for i in range(min_len) 
                           if text_pattern[i] == meter_syllable_pattern[i])
        similarity = matching_chars / max(len(text_pattern), len(meter_syllable_pattern))
        
        if similarity > 0.7:  # Threshold for considering it a match
            matches.append((meter_name, similarity))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)

def main():
    st.title("Arabic Poetry Meter Analyzer محلل البحور الشعرية")
    st.write("Enter a line of Arabic poetry to identify its meter البحر الشعري")
    
    # Text input for the poetry line
    poetry_line = st.text_area("Enter your poetry line here:", "")
    
    if st.button("Analyze"):
        if poetry_line:
            # Get the syllable pattern
            pattern = get_syllable_pattern(poetry_line)
            
            # Find matching meters
            matches = find_matching_meter(pattern)
            
            if matches:
                st.success("Potential meters found!")
                for meter_name, similarity in matches[:3]:  # Show top 3 matches
                    confidence = similarity * 100
                    st.write(f"- {meter_name} (Confidence: {confidence:.1f}%)")
                    st.write(f"  Pattern: {METERS[meter_name]}")
            else:
                st.warning("No matching meter found. Please check the text or try another line.")
                
            # Show the analyzed pattern for debugging
            st.write("Detected syllable pattern:", pattern)
        else:
            st.error("Please enter a line of poetry to analyze.")

if __name__ == "__main__":
    main()
