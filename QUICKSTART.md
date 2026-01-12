# Quick Start Guide - Shaggy Dog Transformer

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
cd shaggy-dog
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `shaggy-dog` directory:
```
REPLICATE_API_TOKEN=your_token_here
SECRET_KEY=generate_a_random_secret_key
```

**To get Replicate API token:**
1. Go to https://replicate.com
2. Sign up/login
3. Go to Account → API Tokens
4. Create a new token
5. Copy and paste into `.env`

**To generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run the App
```bash
python app.py
```

### 4. Open in Browser
Visit: http://localhost:5000

## 🧪 Test the Application

Run the test script:
```bash
python test_app.py
```

## 🚀 Deploy to Render

1. **Push to GitHub** (if not already)
2. **Go to Render.com** and sign up
3. **Create New Web Service**
4. **Connect GitHub repository**
5. **Set environment variables:**
   - `REPLICATE_API_TOKEN` = your token
   - `SECRET_KEY` = your secret key
6. **Deploy!**

See `deployment.md` for detailed instructions.

## 📝 Important Notes

- First image generation may take 30-60 seconds
- Replicate API has rate limits (check your plan)
- Images are stored locally (will be lost on Render restart on free tier)
- For production, use cloud storage (S3, Cloudinary)

## 🐛 Troubleshooting

**Import errors?**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Database errors?**
- Database will be created automatically on first run
- Check file permissions in project directory

**Replicate API errors?**
- Verify token is correct in `.env`
- Check Replicate dashboard for API status
- Ensure you have API credits/quota

**App won't start?**
- Check port 5000 is not in use
- Verify all dependencies installed
- Check for error messages in terminal

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] `.env` file created with tokens
- [ ] Replicate API token obtained
- [ ] App runs locally
- [ ] Can register/login
- [ ] Can upload images (test with Replicate API)

## 🎯 Next Steps

1. Test locally first
2. Customize styling if desired
3. Deploy to Render
4. Set up custom domain (optional)
5. Monitor usage and API costs

Good luck! 🐕
