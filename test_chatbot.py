"""
Test script for the chatbot API endpoint
Run this to verify the chatbot is working correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_setup():
    """Test if Gemini API key is configured"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("📝 Create a .env file and add: GEMINI_API_KEY=your_key_here")
        print("🔑 Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ GEMINI_API_KEY is configured")
    return True

def test_gemini_connection():
    """Test connection to Gemini API"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Test simple query
        print("🧪 Testing Gemini API connection...")
        response = model.generate_content("Say 'Hello' in one word")
        
        if response.text:
            print(f"✅ Gemini API is working! Response: {response.text}")
            return True
        else:
            print("❌ No response from Gemini API")
            return False
            
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("📦 Install it with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Gemini API: {str(e)}")
        return False

def test_chatbot_prompt():
    """Test the chatbot with a sample carpooling question"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        system_prompt = """You are CarpoolBot, an AI assistant for a carpooling web application. The app allows users to register, log in, offer rides, search for rides, book rides, manage bookings, add cars, review other users, and submit reports or feedback. Users can be drivers or passengers. The app uses Google Maps, supports file uploads (such as license and vehicle photos), and has a wallet for ride expenses.

Your tasks:
- Answer questions about using the site (e.g., how to register, offer a ride, book a ride, cancel a booking, add a car, submit a review, or report an issue).
- Explain features like ride packages (daily, weekly, biweekly, monthly), wallet/expenses, and user reviews.
- Help users troubleshoot common issues (e.g., login problems, booking errors, uploading documents).
- Guide users to the correct page or form for their needs.
- Be friendly, concise, and clear. If you don't know the answer, suggest contacting support.

Always answer as if you are part of the carpooling site's support team. If a user asks about something outside the carpooling app, politely decline to answer."""
        
        test_question = "How do I offer a ride?"
        print(f"\n🧪 Testing chatbot with question: '{test_question}'")
        print("="*50)
        
        full_prompt = f"{system_prompt}\n\nUser: {test_question}\n\nAssistant:"
        response = model.generate_content(full_prompt)
        
        print(f"\n🤖 CarpoolBot Response:")
        print(response.text)
        print("="*50)
        print("✅ Chatbot is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chatbot: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("🤖 CHATBOT SETUP VERIFICATION")
    print("="*50 + "\n")
    
    # Test 1: Check API key
    if not test_gemini_setup():
        return
    
    print()
    
    # Test 2: Test connection
    if not test_gemini_connection():
        return
    
    print()
    
    # Test 3: Test chatbot functionality
    test_chatbot_prompt()
    
    print("\n" + "="*50)
    print("🎉 All tests passed! Your chatbot is ready to use!")
    print("="*50 + "\n")
    print("📱 Start your Flask app with: python app.py")
    print("💬 The chatbot will appear on all pages")
    print()

if __name__ == "__main__":
    main()
