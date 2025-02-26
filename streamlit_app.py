import os
import streamlit as st
import json
from openai import OpenAI  # Import OpenAI package

# Load prompt database from JSON file
with open("juese.json", "r", encoding="utf-8") as f:
    prompts_db = json.load(f)

# Initialize OpenAI client with your API key and custom base URL (for Gemini)
client = OpenAI(
    api_key="EMPTY",
    base_url='http://34.28.33.252:6001'
)

st.set_page_config(page_title="hotchat 模型测试")

# Sidebar: Credentials and Prompt Selection
with st.sidebar:
    st.title('hotchat 模型测试')
    st.write('可以用这个app来测不同的system prompt')
    
    # Character Prompt selection
    st.subheader('Character Prompt')
    prompt_type = st.selectbox('Select Prompt Type', ['old', 'new'])
    character = st.selectbox('Select Character', list(prompts_db[prompt_type].keys()))
    selected_prompt = prompts_db[prompt_type][character]
    st.write(f"Selected Prompt for {character} ({prompt_type}):")
    st.write(selected_prompt)
    
    # Create a system prompt based on selection
    system_prompt = f"You're {character}. {selected_prompt}"
    

    # Model parameters (can adjust as needed)
    st.subheader('Model Parameters')
    temp = st.slider('temperature', min_value=0.01, max_value=2.0, value=0.2, step=0.01)
    topp = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.8, step=0.01)
    maxt = st.slider('max_tokens', min_value=100, max_value=2000, value=1000, step=100)

# Initialize or load chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# Helper function to generate responses using the Gemini model
def generate_gemini_response(prompt_input):
    """
    Build the conversation history, append the user's prompt, then call the Gemini model.
    """
    # Build conversation history with system prompt first
    conversation = [{"role": "system", "content": system_prompt}]
    
    # Add user's current prompt
    conversation.append({"role": "user", "content": prompt_input})

    try:
        # API call using custom base URL (Gemini model)
        response = client.chat.completions.create(
            model="gemini-1.5-flash",  # Your Gemini model
            messages=conversation,  # List of messages
            temperature=temp,
            top_p=topp,
            max_tokens=maxt,
            timeout=60,
            stream=True  # Enable streaming
        )
        
        reasoning_content = ""
        content = ""
        
        # Process chunks of the streamed response
        for chunk in response:
            # Check if reasoning_content exists in the chunk
                # Add the content to the result
                content += chunk.choices[0].delta.content

        # Return the complete content
        return content

    except Exception as e:
        return f"Error contacting Gemini model: {e}"

# Handle user prompt input via Streamlit's chat input
if prompt := st.chat_input("Enter your prompt here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a response if the last message is from the user
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = generate_gemini_response(prompt)  # Synchronous call to Gemini API
            placeholder = st.empty()
            full_response = ''
            # For non-streaming, simply display the full response
            full_response = response_text
            placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
