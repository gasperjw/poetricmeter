import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_bahr(poem):
    """Analyze the Bahr meter using OpenAI GPT with explicit thinking process"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are an expert in Arabic prosody (علم العروض). 
                Follow these EXACT steps to analyze the verse:
                
                1. First, write the verse with complete diacritical marks (تشكيل)
                
                2. Perform scansion (التقطيع العروضي):
                   - Split into syllables using traditional symbols (٫)
                   - Mark each syllable as sabab khafif (//), sabab thaqil (///), or watad majmoo (/0/)
                   - Write complete taf'ilah units
                
                3. Compare with standard meters:
                   الطويل: فعولن مفاعيلن فعولن مفاعلن (×٢)
                   البسيط: مستفعلن فاعلن مستفعلن فاعلن (×٢)
                   الوافر: مفاعلتن مفاعلتن فعولن (×٢)
                   الكامل: متفاعلن متفاعلن متفاعلن (×٢)
                   الرجز: مستفعلن مستفعلن مستفعلن (×٢)
                   الرمل: فاعلاتن فاعلاتن فاعلاتن (×٢)
                   السريع: مستفعلن مستفعلن مفعولات
                   المنسرح: مستفعلن مفعولات مستفعلن
                   الخفيف: فاعلاتن مستفعلن فاعلاتن
                
                Format your response EXACTLY as:
                
                **Original with Tashkeel:**
                [Fully voweled verse]
                
                **Scansion Steps:**
                1. Syllable division: [Show syllables separated by ٫]
                2. Metrical units: [Mark each // /// /0/]
                3. Taf'ilah breakdown: [Show complete taf'ilah units]
                
                **Pattern Matching:**
                - Found pattern: [Write the complete metrical pattern]
                - Matches standard: [Show which standard meter this matches]
                
                **Conclusion:**
                [State the Bahr name in bold: **بحر name**]
                
                If NO exact match is found, analyze WHY it doesn't match and respond with 'NO_MATCH' with explanation.
                
                If the verse doesn't match any Bahr, explain why and respond with 'NO_MATCH'"""},
                {"role": "user", "content": poem}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing Bahr: {e}")
        return None

def validate_meter(text, claimed_bahr):
    """Validate that the text actually matches the claimed meter"""
    standard_patterns = {
        "الطويل": "فعولن مفاعيلن فعولن مفاعلن",
        "البسيط": "مستفعلن فاعلن مستفعلن فاعلن",
        "الوافر": "مفاعلتن مفاعلتن فعولن",
        "الكامل": "متفاعلن متفاعلن متفاعلن",
        "الرجز": "مستفعلن مستفعلن مستفعلن",
        "الرمل": "فاعلاتن فاعلاتن فاعلاتن",
        "السريع": "مستفعلن مستفعلن مفعولات",
        "المنسرح": "مستفعلن مفعولات مستفعلن",
        "الخفيف": "فاعلاتن مستفعلن فاعلاتن"
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""Verify if this text EXACTLY matches {claimed_bahr} meter.
                Standard pattern: {standard_patterns.get(claimed_bahr, 'Unknown')}
                
                Return ONLY 'VALID' or 'INVALID' with one line explanation."""},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "INVALID: Validation error"

def extract_bahr_from_analysis(analysis_text):
    """Extract just the Bahr name from the full analysis"""
    if "NO_MATCH" in analysis_text:
        return "NO_MATCH"
    # Look for the Bahr name between ** marks in the Conclusion section
    import re
    match = re.search(r'\*\*(بحر [^*]+)\*\*', analysis_text)
    if match:
        return match.group(1)
    return None

def fit_to_bahr(poem, target_bahr):
    """Attempt to modify the poem to fit the specified Bahr"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""You are an expert in Arabic prosody (علم العروض). 
                Follow these steps to modify the verse to fit {target_bahr}:
                
                1. First identify the current meter pattern (if any)
                2. Map out the target meter pattern exactly:
                   - For طويل: فعولن مفاعيلن فعولن مفاعلن (×٢)
                   - For بسيط: مستفعلن فاعلن مستفعلن فاعلن (×٢)
                   - For وافر: مفاعلتن مفاعلتن فعولن (×٢)
                   - [etc. - use exact pattern needed]
                
                3. Modify the verse following these rules:
                   - Maintain all core words (أسماء وأفعال) possible
                   - Adjust word order to fit meter
                   - Use synonyms of same root when needed
                   - Modify only particles (حروف) when possible
                   - Keep the same rhyme letter (رَوِيّ)
                
                4. Verify the new version by:
                   - Writing complete diacritical marks
                   - Checking syllable by syllable
                   - Confirming exact match to meter
                
                Format your response as:
                **Original:** [original verse]
                **Modification Process:**
                [Explain your modifications]
                **Modified:** [modified verse]
                **Scansion of Modified Verse:**
                [Show the scansion]
                """},
                {"role": "user", "content": poem}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error fitting to Bahr: {e}")
        return None

def generate_response(poem, bahr, original_bahr=None):
    """Generate poetic response using OpenAI GPT"""
    try:
        context = ""
        if original_bahr and original_bahr != bahr:
            context = f"Note: The original poem was in {original_bahr} but has been modified to fit {bahr}."
            
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""You are a classical Arabic poet. Compose a response verse that:
                1. Strictly follows the {bahr} meter
                2. Maintains the original theme
                3. Uses classical Arabic language
                4. Rhymes appropriately
                5. Is grammatically correct
                
                Format your response as:
                **Composition Process:**
                [Explain your thinking]
                
                **Response Verse:**
                [The verse]
                
                **Scansion:**
                [Show the scansion]
                
                {context}"""},
                {"role": "user", "content": poem}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

# Streamlit UI
st.title("Arabic Poetry Meter Analyzer & Generator")
st.markdown("""
<style>
.arabic-text {
    font-size: 20px;
    text-align: right;
    direction: rtl;
}
.analysis-text {
    font-size: 16px;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

poem_input = st.text_area("Enter Arabic Poetry:", height=150, key="poem_input")
preferred_bahr = st.selectbox(
    "Preferred Bahr (optional):",
    ["None", "الطويل", "البسيط", "الوافر", "الكامل", "الرجز", "الرمل", "السريع", "المنسرح", "الخفيف", "المضارع", "المقتضب", "المجتث", "المتقارب", "المتدارك"]
)

if st.button("Analyze & Generate"):
    if poem_input.strip() == "":
        st.error("Please enter some Arabic poetry")
    else:
        with st.spinner("🔍 Analyzing Bahr Meter..."):
            full_analysis = analyze_bahr(poem_input)
            if full_analysis:
                st.markdown("### Meter Analysis:")
                st.markdown(f"<div class='analysis-text'>{full_analysis}</div>", unsafe_allow_html=True)
                
                original_bahr = extract_bahr_from_analysis(full_analysis)
            
        if original_bahr == "NO_MATCH" or (preferred_bahr != "None" and original_bahr != preferred_bahr):
            target_bahr = preferred_bahr if preferred_bahr != "None" else "الطويل"  # Default to Taweel if no preference
            
            st.warning(f"Poetry doesn't match {target_bahr} meter. Attempting to modify...")
            with st.spinner("✍️ Modifying poem to fit meter..."):
                modified_result = fit_to_bahr(poem_input, target_bahr)
                
            if modified_result:
                st.markdown("### Modified Poetry:")
                st.markdown(f"<div class='analysis-text'>{modified_result}</div>", unsafe_allow_html=True)
                
                # Extract modified poem for response generation
                modified_lines = modified_result.split('\n')
                modified_poem = None
                for line in modified_lines:
                    if line.startswith("**Modified:**"):
                        modified_poem = line.replace("**Modified:**", "").strip()
                        break
                
                if modified_poem:
                    with st.spinner("🖋 Composing Response..."):
                        response = generate_response(modified_poem, target_bahr, original_bahr)
                else:
                    st.error("Could not extract modified poem. Please try again.")
            else:
                st.error("Could not modify the poem to fit the meter. Please try different poetry.")
                
        elif original_bahr:
            with st.spinner("🖋 Composing Response..."):
                response = generate_response(poem_input, original_bahr)
                
        if response:
            st.markdown("### Response:")
            st.markdown(f"<div class='analysis-text'>{response}</div>", unsafe_allow_html=True)
            st.balloons()
        else:
            st.error("Could not generate response. Please try again.")

st.markdown("---")
st.markdown("""
### About
This app analyzes Arabic poetry meter (Bahr) and generates matching responses. It provides detailed analysis of the meter detection process and shows the thinking behind modifications and responses.

### Features
- Detailed meter analysis with scansion
- Explanation of thinking process
- Optional preferred meter selection
- Detailed modification process
- Generation of matching responses with explanation
- Preserves meaning and classical style
""")
