import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_bahr(poem):
    """Analyze the Bahr meter using OpenAI GPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in Arabic prosody (علم العروض). Analyze the following verse and think it out then respond with the Arabic name of the Bahr in bold. If the verse doesn't match any Bahr, respond with 'NO_MATCH'. Format: **بحر name** or NO_MATCH"},
                {"role": "user", "content": poem}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing Bahr: {e}")
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
                **Modified:** [modified verse]
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
                {context}
                Format: **[البحر: {bahr}]** followed by the verse"""},
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
            original_bahr = analyze_bahr(poem_input)
            
        if original_bahr == "NO_MATCH" or (preferred_bahr != "None" and original_bahr != preferred_bahr):
            target_bahr = preferred_bahr if preferred_bahr != "None" else "الطويل"  # Default to Taweel if no preference
            
            st.warning(f"Poetry doesn't match {target_bahr} meter. Attempting to modify...")
            with st.spinner("✍️ Modifying poem to fit meter..."):
                modified_result = fit_to_bahr(poem_input, target_bahr)
                
            if modified_result:
                st.markdown("### Modified Poetry:")
                st.markdown(f"<div class='arabic-text'>{modified_result}</div>", unsafe_allow_html=True)
                
                # Extract modified poem for response generation
                modified_poem = modified_result.split("**Modified:**")[-1].strip()
                
                with st.spinner("🖋 Composing Response..."):
                    response = generate_response(modified_poem, target_bahr, original_bahr)
            else:
                st.error("Could not modify the poem to fit the meter. Please try different poetry.")
                
        elif original_bahr:
            st.markdown(f"### Detected Meter: \n<div class='arabic-text'>{original_bahr}</div>", 
                       unsafe_allow_html=True)
            
            with st.spinner("🖋 Composing Response..."):
                response = generate_response(poem_input, original_bahr)
                
        if response:
            st.markdown("### Response:")
            st.markdown(f"<div class='arabic-text'>{response}</div>", unsafe_allow_html=True)
            st.balloons()
        else:
            st.error("Could not generate response. Please try again.")

st.markdown("---")
st.markdown("""
### About
This app analyzes Arabic poetry meter (Bahr) and generates matching responses. If the input doesn't match the desired meter, 
it attempts to modify the poetry while preserving meaning.

### Features
- Detects Arabic poetry meter (Bahr)
- Optional preferred meter selection
- Automatic meter fitting
- Generates matching poetic responses
- Preserves meaning and classical style
""")
