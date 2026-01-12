# Troubleshooting Image Generation

## Issue: No Transformation Happening

If you upload an image but only see the original (no transformations), check the following:

### 1. Verify Replicate API Token

Make sure your `.env` file exists in the `shaggy-dog` directory and contains:

```
REPLICATE_API_TOKEN=r8_your_actual_token_here
SECRET_KEY=your_secret_key_here
```

**Important:** The token should start with `r8_` and be your full Replicate API token from https://replicate.com/account/api-tokens

### 2. Check Server Logs

When you upload an image, check the terminal/console where the Flask app is running. You should see:
- "Replicate API token loaded: r8_..."
- "Generating image with prompt: ..."
- "Downloading image from: ..."
- "Image saved to: ..."

If you see errors, they will be printed there.

### 3. Common Issues

**Issue: "REPLICATE_API_TOKEN not found in environment"**
- Solution: Make sure `.env` file exists in `shaggy-dog` directory
- Solution: Restart the Flask app after creating/updating `.env`

**Issue: "Error generating image: ..."**
- Check your Replicate account has credits/quota
- Verify the API token is correct
- Check Replicate service status

**Issue: Images generate but don't appear**
- Check browser console for JavaScript errors
- Verify images are being saved to `uploads/` directory
- Check file permissions

### 4. Test Replicate API Directly

You can test if your API token works by running:

```python
import os
from dotenv import load_dotenv
import replicate

load_dotenv()
os.environ['REPLICATE_API_TOKEN'] = os.environ.get('REPLICATE_API_TOKEN')

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "a cute dog"}
)

print(output)
```

### 5. Expected Behavior

When working correctly:
1. Upload image → saved to `uploads/`
2. Breed detection → returns breed name
3. Three images generate (this takes 30-60 seconds each)
4. Images appear in gallery

**Note:** Image generation takes time! Each image can take 30-60 seconds. Be patient.

### 6. If Still Not Working

1. Check Replicate dashboard for API usage/errors
2. Verify you have API credits
3. Try a simpler test prompt first
4. Check network connectivity
5. Review server logs for detailed error messages
