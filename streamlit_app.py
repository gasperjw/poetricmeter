import streamlit as st
import openai

# Set up OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

def analyze_bahr(poem):
    """Analyze the Bahr meter using OpenAI GPT"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in Arabic prosody (علم العروض). Analyze the following verse and respond ONLY with the Arabic name of the Bahr in bold. No explanations. Format: **بحر name**"},
                {"role": "user", "content": poem}
            ],
            temperature=0.1
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error analyzing Bahr: {e}")
        return None

def generate_response(poem, bahr):
    """Generate poetic response using OpenAI GPT"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""You are a classical Arabic poet. Compose a response verse that:
1. Strictly follows the {bahr} meter
2. Maintains the original theme
3. Uses classical Arabic language
4. Rhymes appropriately
5. Is grammatically correct

Format: **[البحر: {bahr}]** followed by the verse"""},
                {"role": "user", "content": poem}
            ],
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

# Streamlit UI
st.title("𓂀 Arabic Poetry Meter Analyzer & Generator 𓂀")
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

if st.button("Analyze & Generate"):
    if poem_input.strip() == "":
        st.error("Please enter some Arabic poetry")
    else:
        with st.spinner("🔍 Analyzing Bahr Meter..."):
            bahr = analyze_bahr(poem_input)
            
        if bahr:
            st.markdown(f"### Detected Meter: \n<div class='arabic-text'>{bahr}</div>", unsafe_allow_html=True)
            
            with st.spinner("🖋 Composing Response..."):
                response = generate_response(poem_input, bahr)
                
            if response:
                st.markdown("### Generated Response:")
                st.markdown(f"<div class='arabic-text'>{response}</div>", unsafe_allow_html=True)
                
                # Add audio celebration
                st.balloons()
        else:
            st.error("Could not determine Bahr meter. Please try again.")

st.markdown("---")
st.markdown("""
**Instructions:**
1. Enter classical Arabic poetry in the text area
2. Click the button to analyze the meter
3. Receive a generated response in the same meter
4. (Note: Works best with clear examples of classical meters)
""")
