#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import google.generativeai as genai

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
class GeminiModel:
    def __init__(self, api_key: str):
        genai.configure(api_key = api_key)                                               # Getting responses using the API Key.
        self.model = genai.GenerativeModel("gemini-1.5-flash")                           # Using specific AI Model.
        self.chat_sessions = {}                                                          # Storing user history for better responses.

    # Starting chatting sessions.
    def start_chat(self, user_id: str):
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = self.model.start_chat()
        return self.chat_sessions[user_id]

    # Generate content using the Gemini model.
    def generate_text(self, user_id: str, prompt: str):
        try:
            chat = self.start_chat(user_id)
            response = chat.send_message(prompt)
            return response.text
        
        except Exception as e:
            print(f"❌ Gemini Model Error: {e}")
            return None
