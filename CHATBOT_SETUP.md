# Chatbot Setup Guide

## Overview
The carpooling application now includes an AI-powered chatbot assistant (CarpoolBot) that helps users with questions about using the site, troubleshooting issues, and navigating features.

## Features
- 🤖 AI-powered responses using Google Gemini
- 💬 Real-time chat interface
- 📱 Responsive design (works on mobile and desktop)
- 🎯 Context-aware assistance for carpooling features
- ⚡ Fast and intuitive user experience

## Setup Instructions

### 1. Install Required Package
```bash
pip install google-generativeai
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure Environment Variables
Create a `.env` file in the project root (or update your existing one):

```env
GEMINI_API_KEY=your_actual_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
```

### 4. Run the Application
```bash
python app.py
```

The chatbot will be automatically available on all pages as a floating button in the bottom-right corner.

## Usage

### For Users
1. Click the blue chat icon in the bottom-right corner of any page
2. Type your question or issue
3. Press Enter or click the send button
4. Get instant AI-powered assistance

### Example Questions
- "How do I offer a ride?"
- "What are the different package types?"
- "How do I cancel my booking?"
- "How does the wallet feature work?"
- "I can't upload my license photo, what should I do?"

## Chatbot Capabilities

The chatbot is trained to help with:
- **Registration & Login**: Account creation, password issues, login problems
- **Offering Rides**: Step-by-step guidance on creating ride offers
- **Booking Rides**: How to search, book, and manage bookings
- **Car Management**: Adding cars, uploading documents
- **Reviews**: Submitting and managing reviews
- **Wallet & Expenses**: Understanding cost sharing and expenses
- **Reports**: How to submit emergency reports or feedback
- **Troubleshooting**: Common issues and solutions

## Technical Details

### Backend (app.py)
- **Endpoint**: `POST /chatbot`
- **Request**: `{"message": "user's question"}`
- **Response**: `{"response": "AI's answer"}`
- **Model**: Google Gemini Pro

### Frontend Components
- **HTML**: Chatbot widget in `templates/base.html`
- **CSS**: Styling in `static/css/style.css`
- **JavaScript**: Interactive functionality in `base.html`

### System Prompt
The chatbot uses a carefully crafted system prompt that:
- Defines its role as a carpooling support assistant
- Limits responses to carpooling-related topics
- Maintains a friendly and helpful tone
- Provides clear, concise answers

## Customization

### Modify Chatbot Personality
Edit the system prompt in `app.py` (line ~1960):
```python
system_prompt = """You are CarpoolBot..."""
```

### Change Chatbot Appearance
Edit styles in `static/css/style.css`:
- Colors: Modify `--primary` variable
- Size: Adjust `#chatbot-window` dimensions
- Position: Change `bottom` and `right` values

### Adjust Response Length
Modify the Gemini model configuration:
```python
model = genai.GenerativeModel(
    'gemini-pro',
    generation_config={
        'max_output_tokens': 500,  # Adjust as needed
        'temperature': 0.7
    }
)
```

## Troubleshooting

### Chatbot shows "Service unavailable"
- **Cause**: GEMINI_API_KEY not set or invalid
- **Solution**: Check your `.env` file and API key

### Chatbot not responding
- **Cause**: API quota exceeded or network issues
- **Solution**: Check Google Cloud Console for quota limits

### Import error: No module named 'google.generativeai'
- **Cause**: Package not installed
- **Solution**: Run `pip install google-generativeai`

### Chatbot gives generic answers
- **Cause**: System prompt may need refinement
- **Solution**: Update the system prompt with more specific instructions

## Cost Considerations

### Gemini API Pricing (as of 2024)
- Gemini Pro: **Free tier available**
- Free tier includes: 60 requests per minute
- For high-traffic sites, monitor usage in Google Cloud Console

### Tips to Minimize Costs
1. Implement rate limiting per user
2. Cache common questions/answers
3. Set appropriate token limits
4. Monitor API usage regularly

## Security Best Practices

1. **Never commit API keys** to version control
2. Use **environment variables** for all secrets
3. Implement **rate limiting** to prevent abuse
4. **Sanitize user input** before sending to API
5. **Log errors** but not user messages (privacy)

## Future Enhancements

Potential improvements:
- 🧠 Add conversation history/context
- 📊 Analytics on common questions
- 🌍 Multi-language support
- 🎨 Customizable themes
- 📧 Email transcripts of chat sessions
- 🔔 Proactive notifications and tips

## Support

If you encounter issues with the chatbot:
1. Check this documentation
2. Review server logs
3. Verify API key is valid
4. Check network connectivity
5. Contact support team

## License
Part of the Carpooling Web Application
