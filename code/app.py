from google import genai
import os
from dotenv import load_dotenv
from PIL import Image

# --- 1. Define Placeholder Functions & Client Setup ---
# These are the functions that will be called based on the user's choice.
# You can replace the content of these functions with your Gemini 2.5 logic later.

def setup_client():
    """Loads environment variables and sets up the Gemini client."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file.")
        return None
    print("Gemini client initialized successfully.")
    return genai.Client(api_key=api_key)

def get_text_response(client):
    """Placeholder for the single text response functionality."""
    print("\n>>> You've chosen: Get Text Response")
  
    user_input = input("Enter your prompt: ")
    response = client.models.generate_content(model="gemini-2.5-flash", contents=user_input)
    print(f"Response: {response.text}")


def start_chat_conversation(client):
    """Handles a multi-turn chat conversation."""
    print("\n>>> You've chosen: Start Chat Conversation")
    print("    (Starting a new chat session. Type 'exit' or 'quit' to return to the menu.)")

    try:
        # 1. Create a new chat session. The session will maintain the history.
        chat = client.chats.create(model='gemini-2.5-flash')

        # 2. Start the conversation loop.
        while True:
            user_input = input("You: ")

            # 3. Check for an exit command.
            if user_input.lower() in ['exit', 'quit']:
                print("Ending chat session.")
                break

            # 4. Send the user's message to the chat session.
            response = chat.send_message(message=user_input)
            
            # 5. Print the bot's response.
            print(f"Bot: {response.text}")

    except Exception as e:
        print(f"An error occurred during the chat session: {e}")


def generate_image(client):
    """Placeholder for the image generation functionality."""
    print("\n>>> You've chosen: Generate an Image")
    image_path = input("Enter the path to the image file: ")
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return
    user_prompt = input("Enter your prompt for the image: ")
    response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=[
        user_prompt,
        Image.open(image_path)
    ]
    )
    print(response.text)
# --- 2. Create the Main Application Loop ---

def display_menu():
    """A simple function to display the menu options."""
    print("\n" + "="*40)
    print("="*40)
    print("Please select an option:")
    print("  1. Get a simple Text Response")
    print("  2. Start an interactive Chat Conversation")
    print("  3. Generate an Image")
    print("  4. Exit")
    print("-"*40)


def main():
    """The main function that runs the application."""
    # Initialize the client once at the start
    client = setup_client()
    if not client:
        return # Exit if the client setup failed

    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            get_text_response(client)
        elif choice == '2':
            start_chat_conversation(client)
        elif choice == '3':
            generate_image(client)
        elif choice == '4':
            print("Exiting the application. Goodbye!")
            break  # This exits the while loop and ends the program.
        else:
            print("\n[Error] Invalid choice. Please enter a number between 1 and 4.")
        
        input("\nPress Enter to return to the menu...")


# --- 3. Run the Application ---
# This standard Python construct ensures the main() function is called
# only when the script is executed directly.
if __name__ == "__main__":
    main()
