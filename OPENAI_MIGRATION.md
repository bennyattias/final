# OpenAI Migration Guide

This document describes the migration from Replicate to OpenAI for the Shaggy Dog application.

## What Changed

### ✅ Completed Changes

1. **requirements.txt** - Removed `replicate`, kept `openai`
2. **openai_generator.py** - New module using:
   - GPT-4 Vision (gpt-4o) for breed analysis
   - DALL-E 3 for image generation
   - Threading for parallel image generation
3. **app.py** - Updated to use `openai_generator` instead of `image_generator`
4. **test_openai.py** - New test script for OpenAI integration

### 📝 Environment Variables

**IMPORTANT:** Update your environment variables:

#### Local Development (.env file)
Remove:
```
REPLICATE_API_TOKEN=...
```

Add/Update:
```
OPENAI_API_KEY=sk-your_openai_api_key_here
SECRET_KEY=your_secret_key
```

#### Render Dashboard
1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. **Remove:** `REPLICATE_API_TOKEN`
4. **Add:** `OPENAI_API_KEY` = your OpenAI API key (starts with `sk-`)

### 🔑 Getting OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add it to your `.env` file and Render environment variables

### 💰 API Costs

**Per transformation:**
- GPT-4 Vision (breed analysis): ~$0.01
- DALL-E 3 (3 images @ standard quality): ~$0.12 ($0.04 each)
- **Total: ~$0.13 per transformation**

**With HD quality:**
- DALL-E 3 HD: $0.08 per image
- **Total: ~$0.25 per transformation**

### 🧪 Testing

Run the test script before deploying:

```bash
cd shaggy-dog
python test_openai.py
```

This will:
1. Check if OPENAI_API_KEY is configured
2. Test breed analysis
3. Test image generation (all 3 transformations)

### 🚀 Deployment Steps

1. **Update requirements.txt** ✅ (Already done)
2. **Update .env file** - Remove REPLICATE_API_TOKEN, add OPENAI_API_KEY
3. **Update Render environment** - Remove REPLICATE_API_TOKEN, add OPENAI_API_KEY
4. **Test locally** - Run `python test_openai.py`
5. **Deploy to Render** - Push changes and redeploy
6. **Test on live site** - Upload an image and verify transformations

### 📊 Performance

- **Breed Analysis:** ~2-5 seconds (GPT-4 Vision)
- **Image Generation:** ~10-30 seconds per image (DALL-E 3)
- **Total Time:** ~30-90 seconds for all 3 images (generated in parallel)

### 🔄 What's Different

**Old (Replicate):**
- Used Replicate's Flux model for image generation
- Used face-swap model for final image
- Manual blending for transitions

**New (OpenAI):**
- Uses DALL-E 3 for all image generation
- All 3 images generated in parallel using threading
- More consistent, high-quality results
- Simpler API (single service)

### ⚠️ Important Notes

1. **Old `image_generator.py` still exists** but is no longer used. You can delete it if you want, but keeping it won't hurt.

2. **Rate Limits:** OpenAI has rate limits. If you hit them:
   - Wait a few minutes
   - Check your OpenAI dashboard for usage
   - Consider upgrading your plan

3. **Error Handling:** The new implementation includes better error handling and will fall back to default breed if analysis fails.

4. **Image Quality:** DALL-E 3 produces excellent results. You can switch to `quality="hd"` in `openai_generator.py` if you want higher quality (but it costs more).

### 🐛 Troubleshooting

**Issue: "OPENAI_API_KEY not found"**
- Check your `.env` file exists in `shaggy-dog/` directory
- Verify the key is set correctly (starts with `sk-`)
- Restart your Flask app after updating `.env`

**Issue: "Rate limit exceeded"**
- Wait a few minutes
- Check your OpenAI account usage
- Consider upgrading your plan

**Issue: Images not generating**
- Check server logs for error messages
- Verify API key is valid
- Test with `test_openai.py` script

**Issue: Slow generation**
- DALL-E 3 takes 10-30 seconds per image
- This is normal - images are generated in parallel
- Total time should be ~30-90 seconds for all 3 images

### 📚 Files Changed

- ✅ `requirements.txt` - Removed replicate
- ✅ `openai_generator.py` - New file (replaces image_generator.py functionality)
- ✅ `app.py` - Updated imports
- ✅ `test_openai.py` - New test file
- ⚠️ `image_generator.py` - Old file (can be deleted, but not required)

### ✅ Migration Checklist

- [x] Update requirements.txt
- [ ] Update .env file (local)
- [ ] Update Render environment variables
- [ ] Test locally with test_openai.py
- [ ] Deploy to Render
- [ ] Test on live site
- [ ] (Optional) Delete old image_generator.py

---

**Need Help?** Check the test script output or server logs for detailed error messages.
