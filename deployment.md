# Shaggy Dog Transformer - Deployment Guide

## Deployment to Render

### Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Replicate API token (get from https://replicate.com)

### Step 1: Prepare Your Code

1. Ensure all files are committed to a GitHub repository
2. Make sure `requirements.txt` includes `gunicorn`
3. Verify `render.yaml` is in the project root

### Step 2: Create Render Account and Service

1. Go to https://render.com
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository (or upload code manually)
5. Render will auto-detect Python

### Step 3: Configure Service Settings

Set these settings in Render dashboard:
- **Name:** shaggy-dog
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Instance Type:** Free (or choose paid for better performance)

### Step 4: Add Environment Variables

In Render dashboard, go to your service → Environment tab, add:

1. **REPLICATE_API_TOKEN**
   - Value: Your Replicate API token from https://replicate.com
   - Sync: false (don't sync across environments)

2. **SECRET_KEY**
   - Value: Generate a random string (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Or let Render generate it automatically

3. **PORT** (optional)
   - Render automatically sets this, but you can add it if needed

### Step 5: Configure Custom Domain (Optional)

1. In Render dashboard, go to Settings → Custom Domain
2. Add your domain: `shaggydog.yourdomain.com`
3. Render will provide a CNAME record value
4. Add CNAME record in your domain registrar's DNS:
   - **Type:** CNAME
   - **Name:** shaggydog (or @ for root domain)
   - **Value:** [the value Render provides, e.g., `shaggy-dog.onrender.com`]
   - **TTL:** 3600

### Step 6: Deploy

1. Click "Manual Deploy" → "Deploy latest commit"
2. Or push to your GitHub repository (auto-deploy if enabled)
3. Wait for build to complete (usually 2-5 minutes)
4. Your app will be live at: `https://shaggy-dog.onrender.com` (or your custom domain)

### Step 7: Verify Deployment

1. Visit your app URL
2. Test registration and login
3. Test image upload (note: first request may be slow due to Render's free tier spin-down)

## Important Notes

### Render Free Tier Limitations
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down may take 30-60 seconds
- ⚠️ 750 hours/month free (enough for this project)
- ✅ Includes custom domain support
- ✅ Auto-deploys from GitHub

### File Storage
- **Important:** Render's filesystem is ephemeral
- Uploaded images will be lost on service restart
- For production, implement cloud storage:
  - AWS S3
  - Cloudinary
  - Google Cloud Storage
  - Or use Render's persistent disk (paid plans)

### Database
- SQLite database file will be created automatically
- Database persists on Render's filesystem (until restart on free tier)
- For production, use PostgreSQL (Render offers managed PostgreSQL)

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Check build logs in Render dashboard

### App Crashes
- Check logs in Render dashboard
- Verify environment variables are set
- Ensure `gunicorn` is in requirements.txt

### Images Not Loading
- Check uploads/ directory permissions
- Verify file paths in database
- Check image serving route in app.py

### API Errors
- Verify REPLICATE_API_TOKEN is set correctly
- Check Replicate API quota/limits
- Review error logs in Render dashboard

## Local Development

To run locally:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with:
# REPLICATE_API_TOKEN=your_token_here
# SECRET_KEY=your_secret_key_here

# Run app
python app.py
```

Visit http://localhost:5000

## Support

For issues:
1. Check Render dashboard logs
2. Review application logs
3. Verify environment variables
4. Test Replicate API separately
