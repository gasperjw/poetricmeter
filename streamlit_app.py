import streamlit as st

# Define meters with their basic patterns
METERS = {
    'الطويل': 'VSVS VVSVS VSVS VVSVS',
    'المديد': 'VSVVS VSV VSVVS',
    'البسيط': 'VSSVS VSV VSSVS VSV',
    'الوافر': 'VVSVS VVSVS VSV',
    'الكامل': 'VVVVS VVVVS VVVVS',
    'الهزج': 'VVSVS VVSVS',
    'الرجز': 'VSSVS VSSVS VSSVS',
    'الرمل': 'VSVVS VSVVS VSVVS',
    'السريع': 'VSSVS VSSVS VSV',
    'المنسرح': 'VSSVS VSVVS VSSVS',
    'الخفيف': 'VSVVS VSSVS VSVVS',
    'المضارع': 'VVSVS VSVVS',
    'المقتضب': 'VSVVS VSSVS',
    'المجتث': 'VSSVS VSVVS',
    'المتقارب': 'VSVS VSVS VSVS VSVS',
    'المتدارك': 'VSV VSV VSV VSV'
}

def find_meter(pattern: str) -> list:
    """Find matching meters for a given pattern."""
    matches = []
    user_pattern = pattern.replace(' ', '')
    
    for meter, meter_pattern in METERS.items():
        base_pattern = meter_pattern.replace(' ', '')
        if user_pattern == base_pattern:
            matches.append(meter)
    
    return matches

def main():
    st.title("Arabic Meter Pattern Matcher محلل البحور الشعرية")
    
    st.markdown("""
    ### Instructions التعليمات
    1. Mark each syllable in your line as:
       - V (متحرك) for short syllables
       - S (ساكن) for long syllables
    2. Separate feet with spaces
    
    Example for الطويل (قفا نبك):
    ```
    VSVS VVSVS VSVS VVSVS
    ```
    """)

    # Example button
    if st.button("Show me examples"):
        st.markdown("""
        Here are some examples:
        
        1. قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِلِ (الطويل)
        ```
        VSVS VVSVS VSVS VVSVS
        ```
        
        2. الشِّعْرُ دِيوَانُ العَرَب (الوافر)
        ```
        VVSVS VVSVS VSV
        ```
        """)

    # Input for pattern
    pattern = st.text_input(
        "Enter the pattern:",
        placeholder="VSVS VVSVS VSVS VVSVS"
    ).upper()

    if st.button("Find Meter"):
        if not pattern:
            st.error("Please enter a pattern")
            return
            
        # Validate input
        if not all(c in 'VS ' for c in pattern):
            st.error("Pattern should only contain V, S, and spaces")
            return
            
        matches = find_meter(pattern)
        
        if matches:
            st.success("Found matching meter(s)!")
            for meter in matches:
                st.write(f"- {meter}")
                st.write(f"  Standard pattern: {METERS[meter]}")
        else:
            st.warning("No exact match found. Double-check your pattern.")
            st.info("Make sure you've marked all syllables correctly and included spaces between feet.")

if __name__ == "__main__":
    main()
