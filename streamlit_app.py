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
                Analyze the following verse by:
                1. Writing out the scansion (التقطيع العروضي)
                2. Identifying the pattern of long and short syllables
                3. Comparing with known Bahr patterns
                4. Explaining your reasoning
                
                Format your response as:
                **Scansion:**
                [Write the scansion here]
                
                **Analysis:**
                [Explain your thinking process]
                
                **Conclusion:**
                [State the Bahr name in bold: **بحر name**]
                
                If the verse doesn't match any Bahr, explain why and respond with 'NO_MATCH'"""},
                {"role": "user", "content": poem}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing Bahr: {e}")
        return None

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
                Modify the given verse to fit the {target_bahr} meter while:
                1. Preserving the original meaning as much as possible
                2. Maintaining classical Arabic language
                3. Ensuring grammatical correctness
                4. Keeping the rhyme scheme if possible
                
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
