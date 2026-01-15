# Quick Start Guide - Chatbot Feature

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install google-generativeai
```

### Step 2: Set Up API Key
1. Get your free Gemini API key: https://makersuite.google.com/app/apikey
2. Create a `.env` file in your project root:
```env
GEMINI_API_KEY=your_api_key_here
```

### Step 3: Run the App
```bash
python app.py
```

That's it! The chatbot will appear on all pages as a blue floating button in the bottom-right corner.

## 📱 How to Use

1. **Click** the chat icon
2. **Type** your question (e.g., "How do I offer a ride?")
3. **Get** instant AI-powered help!

## 💬 What Can the Chatbot Help With?

- ✅ How to register and login
- ✅ Offering rides
- ✅ Booking rides
- ✅ Adding your car
- ✅ Managing bookings
- ✅ Submitting reviews
- ✅ Understanding ride packages (daily, weekly, monthly)
- ✅ Wallet and expense tracking
- ✅ Troubleshooting common issues

## 🎨 Features

- **Smart AI**: Powered by Google Gemini
- **Always Available**: Works on all pages
- **Mobile Friendly**: Responsive design
- **Fast**: Instant responses
- **Helpful**: Trained specifically for carpooling features

## ⚠️ Troubleshooting

**Chatbot says "Service unavailable"?**
- Make sure you've set your `GEMINI_API_KEY` in the `.env` file

**Can't see the chat button?**
- Clear your browser cache and refresh the page

**Getting errors?**
- Check that `google-generativeai` is installed
- Verify your API key is valid

## 📚 Need More Help?

See the full documentation: [CHATBOT_SETUP.md](CHATBOT_SETUP.md)

---

**Note**: The Gemini API has a free tier with generous limits. Perfect for getting started!
