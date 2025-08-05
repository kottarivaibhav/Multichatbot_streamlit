import streamlit as st
from google import genai
import os
from dotenv import load_dotenv
from PIL import Image

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="MultiBot - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Client Setup ---
@st.cache_resource
def setup_client():
    """Loads environment variables and sets up the Gemini client."""
    try:
        # Try to get API key from Streamlit secrets first (for cloud deployment)
        api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fallback to environment variable (for local development)
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY not found. Please add it to Streamlit secrets or .env file.")
        st.stop()
    
    return genai.Client(api_key=api_key)

# --- Core Functions ---
#def get_text_response(client, user_input):
    """Get a single text response from Gemini."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=user_input
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def get_text_response_streaming(client, user_input, placeholder):
    """Get a streaming text response from Gemini."""
    try:
        # Check if streaming is supported
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=user_input
        )
        
        # Simulate streaming effect by displaying text progressively
        full_text = response.text
        displayed_text = ""
        
        for char in full_text:
            displayed_text += char
            placeholder.markdown(displayed_text + "▋")  # Add cursor
            import time
            time.sleep(0.02)  # Small delay for typing effect
        
        placeholder.markdown(full_text)  # Final text without cursor
        return full_text
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        placeholder.error(error_msg)
        return error_msg
        

def analyze_image(client, image, prompt):
    """Analyze an uploaded image with Gemini."""
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, image]
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
    
# Adding a streaming response for chat conversation
def chat_response_streaming(chat_session, user_message, placeholder):
    """Get a streaming chat response."""
    try:
        response = chat_session.send_message(
            message=user_message
        )
        
        # Simulate streaming effect by displaying text progressively
        full_text = response.text
        displayed_text = ""
        
        import time
        for char in full_text:
            displayed_text += char
            placeholder.markdown(f"**🤖 Bot:** {displayed_text}▋")  # Add cursor effect
            time.sleep(0.02)  # Small delay for typing effect
        
        placeholder.markdown(f"**🤖 Bot:** {full_text}")  # Final response
        return full_text
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        placeholder.error(error_msg)
        return error_msg    

# --- Main Streamlit App ---
def main():
    # Initialize client
    client = setup_client()
    
    # App Header
    st.title("🤖 MultiBot - AI Assistant")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("🚀 Features")
    app_mode = st.sidebar.selectbox(
        "Choose a feature:",
        ["💬 Text Chat", "🔄 Conversation", "🖼️ Image Analysis"]
    )
    
     
    # Feature 1: Simple Text Response with Streaming
    if app_mode == "💬 Text Chat":
        st.header("💬 Get Text Response for a single query")
        st.markdown("Ask me anything and get an instant response!")
        
        user_input = st.text_area(
            "Enter your prompt:",
            placeholder="Type your question here...",
            height=50
        )
        
        if st.button("🚀 Generate Response", type="primary"):
            if user_input.strip():
                st.success("✅ Generating response...")
                st.markdown("### 🤖 AI Response:")
                
                # Create placeholder for streaming response
                response_placeholder = st.empty()
                
                # Get streaming response
                response = get_text_response_streaming(client, user_input, response_placeholder)
                
            else:
                st.warning("⚠️ Please enter a prompt first!")
   # Feature 2: Interactive Chat with Streaming
    elif app_mode == "🔄 Conversation":
        st.header("🔄 Interactive Chat")
        st.markdown("Have a continuous conversation with the AI!")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            st.session_state.chat_session = None
        
        # Initialize chat message input state
        if "chat_message_input" not in st.session_state:
            st.session_state.chat_message_input = ""
        
        # Initialize chat session
        if st.session_state.chat_session is None:
            try:
                st.session_state.chat_session = client.chats.create(model='gemini-2.5-flash')
                st.success("✅ New chat session started!")
            except Exception as e:
                st.error(f"❌ Error creating chat session: {e}")
                st.stop()
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Chat History:")
            for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
                st.markdown(f"**You:** {user_msg}")
                st.markdown(f"**🤖 Bot:** {bot_msg}")
                st.markdown("---")
        
        # Chat input with session state control
        user_message = st.text_input(
            "Type your message:",
            key="chat_input",
            value=st.session_state.chat_message_input
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📤 Send Message", type="primary"):
                if user_message.strip():
                    try:
                        # Show user message immediately
                        st.markdown(f"**You:** {user_message}")
                        
                        # Create placeholder for streaming response
                        response_placeholder = st.empty()
                        
                        # Get streaming response
                        response_text = chat_response_streaming(
                            st.session_state.chat_session, 
                            user_message, 
                            response_placeholder
                        )
                        
                        # Add to chat history
                        st.session_state.chat_history.append(
                            (user_message, response_text)
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    
                    # Clear the input field (outside try block so it always executes)
                    st.session_state.chat_message_input = ""
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a message first!")
        
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.session_state.chat_session = None
                st.session_state.chat_message_input = ""  # Clear input as well
                st.rerun()
    elif app_mode == "🖼️ Image Analysis":
        st.header("🖼️ Image Analysis")
        st.markdown("Upload an image and ask questions about it!")
        
        uploaded_file = st.file_uploader(
            "Choose an image file:",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Upload an image to analyze"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Prompt for image analysis
            image_prompt = st.text_area(
                "What would you like to know about this image?",
                placeholder="Describe what you see, identify objects, analyze the scene, etc.",
                height=100
            )
            
            if st.button("🔍 Analyze Image", type="primary"):
                if image_prompt.strip():
                    with st.spinner("🔍 Analyzing image..."):
                        response = analyze_image(client, image, image_prompt)
                    
                    st.success("✅ Analysis complete!")
                    st.markdown("### 🤖 AI Analysis:")
                    st.markdown(response)
                else:
                    st.warning("⚠️ Please enter a prompt for image analysis!")
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; padding: 20px;'>
                🤖 MultiBot powered by Google Gemini AI<br>
            © Built by Vaibhav Kottari
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Run the App ---
if __name__ == "__main__":
    main()
