import os
import openai
import threading
import urllib.request
import base64
from PIL import Image, ImageDraw, ImageFilter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key from environment
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if OPENAI_API_KEY:
    print(f"OpenAI API key loaded: {OPENAI_API_KEY[:10]}...")
else:
    print("WARNING: OPENAI_API_KEY not found in environment!")

def image_to_base64(image_path):
    """Convert image file to base64 encoded string"""
    try:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return image_base64
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

def download_image(url, save_path):
    """Download image from URL and save locally"""
    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"Image downloaded and saved to: {save_path}")
        return save_path
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def analyze_dog_breed(image_path):
    """
    Analyze the uploaded image to determine the closest dog breed.
    Uses OpenAI GPT-4 Vision to analyze facial features.
    """
    try:
        if not OPENAI_API_KEY:
            print("OpenAI API key not found, using default breed")
            return "Golden Retriever"
        
        # Read the image and encode it
        image_base64 = image_to_base64(image_path)
        if not image_base64:
            print("Failed to encode image, using default breed")
            return "Golden Retriever"
        
        # Use GPT-4 Vision to analyze the image
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Determine image MIME type
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png" if ext == '.png' else "image/jpeg"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that matches people to dog breeds in a fun, creative way. This is for a lighthearted app that creates fun transformations."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Look at this portrait photo. If you had to match this person to a dog breed based on their general appearance, expression, and vibe, which single dog breed would you choose? This is for a fun creative app. Just return the breed name only, like 'Golden Retriever' or 'German Shepherd'. No explanation needed."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=30
        )
        
        breed = response.choices[0].message.content.strip()
        print(f"Detected breed: {breed}")
        
        # If GPT-4 refuses or returns an error message, use a default breed
        if "sorry" in breed.lower() or "can't" in breed.lower() or "cannot" in breed.lower():
            print("GPT-4 refused, using default breed: Golden Retriever")
            return "Golden Retriever"
        
        return breed
        
    except Exception as e:
        print(f"Error analyzing breed: {e}")
        import traceback
        traceback.print_exc()
        # Return a default breed if analysis fails
        return "Golden Retriever"

def generate_single_transformation_image(prompt, output_path):
    """
    Generate a single transformation image using DALL-E 3.
    Returns the path to the saved image or None on error.
    """
    try:
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY not set in environment")
            return None
        
        print(f"Generating image with DALL-E 3...")
        print(f"Prompt preview: {prompt[:100]}...")
        
        # Use OpenAI DALL-E 3 to generate the image
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get the image URL from the response
        image_url = response.data[0].url
        
        if image_url:
            print(f"Downloading image from: {image_url}")
            download_image(image_url, output_path)
            return output_path
        else:
            print("ERROR: No image URL returned from OpenAI")
            return None
            
    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None

def edit_image_with_dog_head(human_image_path, dog_head_image_path, breed, output_path, transformation_level=1.0):
    """
    Use GPT-Image-1 to edit the human image by replacing the head with the dog head.
    This model accepts multiple images as input - we send both the human image and dog head image!
    """
    try:
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY not set in environment")
            return None
        
        print(f"[GPT-Image-1] Editing image (transformation level: {transformation_level})...")
        print(f"[GPT-Image-1] Sending both images: human image and dog head image")
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Create edit prompt based on transformation level
        if transformation_level == 0.3:
            edit_prompt = f"Take the dog head from the second image and use it to replace the human head in the first image, showing subtle transformation (about 30%). The face structure remains mostly human but starting to show canine characteristics from the dog head - slight furry texture appearing on skin around face, ears just beginning to shift toward {breed} dog ears, eyes showing hints of canine characteristics while remaining mostly human-shaped. Keep everything else from the first image exactly the same (body, clothing, pose, background, lighting). Match the dog's expression from the second image to the human's original expression from the first image."
        elif transformation_level == 0.7:
            edit_prompt = f"Take the dog head from the second image and use it to replace the human head in the first image, showing significant transformation (about 70%). The dog head from the second image should be prominently featured with fully formed {breed} ears, significant fur coverage, developing snout, and canine eye structure. The dog's expression from the second image should match the human's original expression from the first image. Keep everything else from the first image exactly the same (body, clothing, pose, background, lighting). Make the transition from dog head to human neck look natural and anatomically correct."
        else:  # 1.0
            edit_prompt = f"Take the {breed} dog head from the second image and use it to completely replace the human head in the first image. The dog head should be fully formed, expressive, and intelligent-looking with detailed {breed} characteristics as shown in the second image. The dog's expression from the second image should match the human's original expression from the first image. Keep everything else from the first image exactly the same (body, clothing, pose, background, lighting). Make the transition from dog head to human neck look completely natural and anatomically correct. Match the lighting on the dog head to the lighting in the first image."
        
        # Open image files as file objects (required by API)
        human_image_file = open(human_image_path, 'rb')
        dog_image_file = open(dog_head_image_path, 'rb')
        
        try:
            # Get file sizes for logging and validation
            human_image_file.seek(0, 2)  # Seek to end
            human_size = human_image_file.tell()
            human_image_file.seek(0)  # Reset to beginning
            
            dog_image_file.seek(0, 2)  # Seek to end
            dog_size = dog_image_file.tell()
            dog_image_file.seek(0)  # Reset to beginning
            
            # Validate file sizes (API limit: 50MB per image)
            MAX_SIZE = 50 * 1024 * 1024  # 50MB in bytes
            if human_size > MAX_SIZE:
                print(f"[GPT-Image-1] ERROR: Human image too large ({human_size} bytes > {MAX_SIZE} bytes)")
                return None
            if dog_size > MAX_SIZE:
                print(f"[GPT-Image-1] ERROR: Dog image too large ({dog_size} bytes > {MAX_SIZE} bytes)")
                return None
            
            print("Attempting GPT-Image-1 with file objects...")
            print(f"Human image size: {human_size} bytes ({human_size / 1024 / 1024:.2f} MB)")
            print(f"Dog image size: {dog_size} bytes ({dog_size / 1024 / 1024:.2f} MB)")
            print(f"Prompt length: {len(edit_prompt)} chars")
            
            # Try GPT-Image-1 first, if it fails try gpt-image-1-mini
            models_to_try = ["gpt-image-1", "gpt-image-1-mini"]
            response = None
            last_error = None
            
            for model_name in models_to_try:
                try:
                    print(f"Trying model: {model_name}...")
                    # API expects a list of file objects opened in binary mode
                    response = client.images.edit(
                        model=model_name,
                        image=[human_image_file, dog_image_file],  # List of file objects
                        prompt=edit_prompt,
                        size="1024x1024",
                        input_fidelity="high"
                        # Note: response_format parameter is not supported for images.edit()
                        # The API returns URLs by default in the response.data[0].url field
                    )
                    print(f"[GPT-Image-1] Successfully got response from {model_name}")
                    break
                except Exception as model_error:
                    print(f"[GPT-Image-1] Model {model_name} failed: {model_error}")
                    last_error = model_error
                    # Reset file pointers for next attempt
                    human_image_file.seek(0)
                    dog_image_file.seek(0)
                    continue
            
            if not response:
                raise Exception(f"All models failed. Last error: {last_error}")
            
            # Debug: print response structure
            print(f"[GPT-Image-1] Response received. Type: {type(response)}")
            
            # Get the image from the response
            # Response structure: response.data[0].url or response.data[0].b64_json
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                first_item = response.data[0]
                
                # Check for URL first
                if hasattr(first_item, 'url'):
                    image_url = first_item.url
                    if image_url:
                        print(f"[GPT-Image-1] Got image URL, downloading...")
                        download_image(image_url, output_path)
                        print(f"[GPT-Image-1] Image saved to: {output_path}")
                        return output_path
                    else:
                        print("[GPT-Image-1] URL field exists but is None")
                
                # Check for base64 JSON
                if hasattr(first_item, 'b64_json'):
                    b64_data = first_item.b64_json
                    if b64_data:
                        print("[GPT-Image-1] Got base64 image data, saving directly...")
                        import base64
                        image_data = base64.b64decode(b64_data)
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        print(f"[GPT-Image-1] Image saved to: {output_path}")
                        return output_path
                    else:
                        print("[GPT-Image-1] b64_json field exists but is None")
                
                # If we get here, neither url nor b64_json has a value
                print(f"[GPT-Image-1] ERROR: Response item has url={getattr(first_item, 'url', 'N/A')} and b64_json={getattr(first_item, 'b64_json', 'N/A')}")
                return None
            else:
                print(f"[GPT-Image-1] ERROR: Response has no data or data is empty")
                return None
                
        except Exception as e:
            # If GPT-Image-1 is not available, fall back to prompt-based generation
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"[GPT-Image-1] API error: {error_type}: {error_msg}")
            
            # Check if it's a model availability issue
            if "model" in error_msg.lower() or "not found" in error_msg.lower() or "not available" in error_msg.lower():
                print("[GPT-Image-1] Model may not be available in your account yet.")
                print("[GPT-Image-1] This model was released in April 2025. You may need to:")
                print("[GPT-Image-1] 1. Check if your OpenAI account has access to GPT-Image-1")
                print("[GPT-Image-1] 2. Try using 'gpt-image-1-mini' instead")
                print("[GPT-Image-1] 3. Or wait for model availability")
            
            print("[GPT-Image-1] Will fall back to prompt-based generation...")
            return None
        finally:
            # Always close the file objects
            human_image_file.close()
            dog_image_file.close()
            
    except Exception as e:
        print(f"Error editing image: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_dog_head_image(breed, user_image_path, output_path):
    """
    Generate a dog head image using DALL-E 3 that matches the user's image characteristics.
    """
    try:
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY not set in environment")
            return None
        
        # First, analyze the user's image to get characteristics
        print("Analyzing user image for dog head generation...")
        image_base64 = image_to_base64(user_image_path)
        if not image_base64:
            print("Failed to encode user image")
            return None
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        ext = os.path.splitext(user_image_path)[1].lower()
        mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png" if ext == '.png' else "image/jpeg"
        
        # Get description of user's features for better matching
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that describes portrait photos for creative image generation."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this portrait in 2-3 short phrases focusing on: lighting (bright, soft, dramatic), angle (front-facing, side, etc.), expression (serious, smiling, neutral), and overall mood. Keep it brief."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50
            )
            user_context = response.choices[0].message.content.strip()
            if "sorry" in user_context.lower() or "can't" in user_context.lower():
                user_context = "professional portrait, front-facing, neutral expression"
            print(f"User image context: {user_context}")
        except Exception as e:
            print(f"Could not analyze user image, using default context: {e}")
            user_context = "professional portrait, front-facing, neutral expression"
        
        # Generate dog head with matching characteristics
        prompt = f"""A photorealistic close-up portrait of a {breed} dog's head and upper neck, looking directly at the camera. The dog should have an expressive, intelligent look. Match the style: {user_context}. Professional pet photography, studio lighting, high quality, detailed fur texture, clear background, headshot composition."""
        
        print(f"Generating {breed} dog head image...")
        dog_head_path = generate_single_transformation_image(prompt, output_path)
        return dog_head_path
        
    except Exception as e:
        print(f"Error generating dog head: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_composite_prompt_from_images(human_image_path, dog_head_image_path, breed, transformation_level):
    """
    Use GPT-4 Vision to analyze both images and create a detailed prompt for DALL-E 3
    that will place the dog head on the human body.
    """
    try:
        if not OPENAI_API_KEY:
            return None
        
        print(f"Analyzing both images to create composite prompt (transformation level: {transformation_level})...")
        
        human_base64 = image_to_base64(human_image_path)
        dog_base64 = image_to_base64(dog_head_image_path)
        
        if not human_base64 or not dog_base64:
            print("Failed to encode images")
            return None
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        ext_human = os.path.splitext(human_image_path)[1].lower()
        ext_dog = os.path.splitext(dog_head_image_path)[1].lower()
        mime_human = "image/jpeg" if ext_human in ['.jpg', '.jpeg'] else "image/png" if ext_human == '.png' else "image/jpeg"
        mime_dog = "image/jpeg" if ext_dog in ['.jpg', '.jpeg'] else "image/png" if ext_dog == '.png' else "image/jpeg"
        
        # Determine transformation description based on level
        if transformation_level == 0.3:
            trans_desc = "Beginning to show subtle dog features (about 30% transformation). Face structure remains mostly human but starting to show canine characteristics. Slight furry texture appearing on skin around face. Ears just beginning to shift toward dog ears. Eyes showing hints of canine characteristics while remaining mostly human-shaped."
        elif transformation_level == 0.7:
            trans_desc = "Significant transformation (about 70%). Dog head prominently featured with fully formed dog ears. Significant fur coverage, developing snout. Canine eye structure and expression."
        else:  # 1.0
            trans_desc = "Complete transformation (100%). Fully formed dog head replacing the human head."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes images and creates detailed prompts for image generation. You will see two images: a human portrait and a dog head. Your task is to create a detailed prompt that tells an image generator how to place the dog head on the human body while keeping everything else exactly the same."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""I have two images:
- Image 1: A human portrait photo
- Image 2: A {breed} dog head portrait

I want to create a new image where the dog head from Image 2 replaces the human head in Image 1, but everything else (body, clothing, pose, background, lighting) stays exactly the same from Image 1.

Transformation level: {trans_desc}

Please create a detailed, specific prompt for an image generator (DALL-E 3) that will:
1. Take the dog head characteristics from Image 2 (the {breed} dog head)
2. Place it on the human body from Image 1
3. Keep the human's body, clothing, pose, background, and lighting exactly as they appear in Image 1
4. Make the transition from dog head to human neck look natural and anatomically correct
5. Match the lighting on the dog head to the lighting in the human image
6. Ensure the dog's expression matches the human's original expression

Format your response as a clear, detailed prompt that can be used directly with DALL-E 3. Be very specific about:
- The dog head characteristics (from Image 2)
- The human body, clothing, pose details (from Image 1)
- The background and lighting (from Image 1)
- How the dog head should be positioned and integrated
- The natural transition at the neck

Start your response with "Photorealistic studio portrait." and structure it clearly."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_human};base64,{human_base64}"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_dog};base64,{dog_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            prompt = response.choices[0].message.content.strip()
            if "sorry" in prompt.lower() or "can't" in prompt.lower() or "cannot" in prompt.lower():
                print("GPT-4 refused, using fallback prompt")
                return None
            print(f"Generated composite prompt: {prompt[:150]}...")
            return prompt
        except Exception as e:
            print(f"Could not create composite prompt: {e}")
            return None
        
    except Exception as e:
        print(f"Error creating composite prompt: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_image_characteristics(image_path):
    """
    Analyze the human image to extract detailed descriptive traits for regeneration.
    Returns a structured description with subject, body, lighting, and style details.
    """
    try:
        if not OPENAI_API_KEY:
            return None
        
        print("Analyzing image characteristics...")
        image_base64 = image_to_base64(image_path)
        if not image_base64:
            return None
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png" if ext == '.png' else "image/jpeg"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes portrait photos to extract visual characteristics for photorealistic image generation. Provide structured, specific details."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this portrait photo and provide a structured description. Format your response with these sections:

Subject:
- Gender and approximate age (e.g., "male, early-to-mid 30s" or "female, mid-20s")
- Face shape (e.g., "oval", "round", "angular", "narrow")
- Hair description (e.g., "short dark brown hair", "long blonde hair", "bald")
- Facial expression (e.g., "friendly, confident smile", "serious professional", "calm and neutral")
- Eye characteristics (e.g., "bright eyes", "warm expression", "alert gaze", "kind eyes")
- Facial features (e.g., "strong jawline", "soft features", "prominent cheekbones", "gentle expression")

Body:
- Clothing description with colors and details (e.g., "wearing a navy blue business suit, white shirt and patterned tie" or "casual t-shirt and jeans")
- Pose and posture (e.g., "arms crossed", "standing straight", "leaning slightly", "hands in pockets")

Lighting:
- Lighting style (e.g., "soft studio lighting", "bright natural light", "dramatic shadows", "even studio illumination")
- Light direction if visible

Background:
- Background description (e.g., "clean white background", "blurred office setting", "outdoor scene", "neutral gray background")

Camera:
- Camera angle (e.g., "front-facing", "slight side angle", "head-on portrait")

Be specific about colors, textures, and details. Do not identify the person, only describe visual characteristics. Pay special attention to facial expression and eye characteristics as these will be important for matching."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            description = response.choices[0].message.content.strip()
            if "sorry" in description.lower() or "can't" in description.lower():
                description = """Subject:
- Person, front-facing portrait
- Neutral expression

Body:
- Professional clothing
- Standing straight

Lighting:
- Soft studio lighting

Background:
- Clean background

Camera:
- Front-facing"""
            print(f"Image analysis: {description[:150]}...")
            return description
        except Exception as e:
            print(f"Could not analyze image, using default: {e}")
            return """Subject:
- Person, front-facing portrait
- Neutral expression

Body:
- Professional clothing
- Standing straight

Lighting:
- Soft studio lighting

Background:
- Clean background

Camera:
- Front-facing"""
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return """Subject:
- Person, front-facing portrait
- Neutral expression

Body:
- Professional clothing
- Standing straight

Lighting:
- Soft studio lighting

Background:
- Clean background

Camera:
- Front-facing"""


def generate_transformation_images(image_path, breed, user_id, timestamp):
    """
    Generate 3 transformation images using a hybrid approach:
    1. Generate a dog head image with DALL-E 3
    2. Use GPT-Image-1 (if available) to edit the human image by replacing the head
    3. If GPT-Image-1 is not available, use GPT-4 Vision to create detailed prompts for DALL-E 3
    
    1. Transition (30% transformation - dog head somewhat integrated on human body)
    2. Final (100% transformation - dog head fully integrated on human body)
    3. Full Dog (complete dog body, no human in picture)
    """
    base_path = f"uploads/{user_id}_{timestamp}"
    dog_head_path = f"{base_path}_dog_head.png"
    trans1_path = f"{base_path}_transition1.png"
    final_path = f"{base_path}_final.png"
    full_dog_path = f"{base_path}_full_dog.png"
    
    print(f"Step 1: Generating {breed} dog head image...")
    # First, generate the dog head image
    dog_path = generate_dog_head_image(breed, image_path, dog_head_path)
    
    if not dog_path or not os.path.exists(dog_path):
        print("ERROR: Failed to generate dog head image")
        return (None, None, None)
    
    print(f"Step 2: Dog head generated. Now creating transformations...")
    
    # Try using GPT-Image-1 for image editing (if available)
    # This model can accept images as input!
    results = {}
    errors = {}
    
    def generate_trans1():
        """Generate transition 1 (30% transformation)"""
        try:
            print("=" * 60)
            print("Thread 1: Generating transition 1 (30% transformation)")
            print("=" * 60)
            # Try GPT-Image-1 first
            print("[METHOD 1] Attempting GPT-Image-1 (direct image editing)...")
            result = edit_image_with_dog_head(image_path, dog_path, breed, trans1_path, transformation_level=0.3)
            if result:
                print("✓ [SUCCESS] Transition 1 generated using GPT-Image-1")
            else:
                # Fall back to prompt-based generation using GPT-4 Vision
                print("[METHOD 2] GPT-Image-1 failed, trying GPT-4 Vision prompt generation...")
                prompt = create_composite_prompt_from_images(image_path, dog_path, breed, 0.3)
                if prompt:
                    print("[METHOD 2] Using GPT-4 Vision generated prompt with DALL-E 3...")
                    result = generate_single_transformation_image(prompt, trans1_path)
                    if result:
                        print("✓ [SUCCESS] Transition 1 generated using GPT-4 Vision + DALL-E 3")
                else:
                    # If GPT-4 Vision refused, use analyze_image_characteristics as fallback
                    print("[METHOD 3] GPT-4 Vision refused, trying image analysis fallback...")
                    image_desc = analyze_image_characteristics(image_path)
                    if image_desc:
                        print("[METHOD 3] Using image analysis with DALL-E 3...")
                        prompt = f"""Photorealistic studio portrait.

Subject:
{image_desc}

Body:
- Human body with visible human shoulders, neck, and clothing
- Posture and clothing remain completely human and unchanged

Head:
- {breed} dog head somewhat integrated (about 30% transformation)
- Face structure remains mostly human but starting to show canine characteristics
- Slight furry texture appearing on skin around face
- Ears just beginning to shift toward {breed} dog ears
- Eyes showing hints of canine characteristics while remaining mostly human-shaped
- Dog head is beginning to replace the human head but not fully integrated yet
- Natural transition beginning from dog head to human neck

Style:
- Ultra-realistic photography
- Shallow depth of field
- No illustration or cartoon
- High detail, seamless transformation"""
                        result = generate_single_transformation_image(prompt, trans1_path)
                        if result:
                            print("✓ [SUCCESS] Transition 1 generated using Image Analysis + DALL-E 3")
                    else:
                        # Final fallback: simple prompt without image analysis
                        print("[METHOD 4] Image analysis failed, using simple fallback prompt...")
                        prompt = f"""Photorealistic studio portrait of a {breed} dog head somewhat integrated on a human body (about 30% transformation). The dog head is beginning to replace the human head but not fully integrated yet - face structure remains mostly human but starting to show subtle canine characteristics, slight furry texture appearing on skin around face, ears just beginning to shift toward {breed} dog ears, eyes showing hints of canine characteristics while remaining mostly human-shaped. The human body, clothing, pose, and background remain completely unchanged. Natural transition beginning from dog head to human neck. Ultra-realistic photography style, shallow depth of field, high detail, seamless transformation."""
                        result = generate_single_transformation_image(prompt, trans1_path)
                        if result:
                            print("✓ [SUCCESS] Transition 1 generated using Simple Fallback + DALL-E 3")
            results['trans1'] = result
            if result:
                print("✓ Thread 1: Transition 1 completed successfully")
            else:
                errors['trans1'] = "Failed to generate transition 1"
                print("✗ Thread 1: Transition 1 FAILED - all methods exhausted")
        except Exception as e:
            errors['trans1'] = str(e)
            print(f"Thread 1: Error generating transition 1: {e}")
    
    def generate_full_dog():
        """Generate full dog image (complete dog body, using the same dog head from previous images)"""
        try:
            print("=" * 60)
            print("Thread 2: Generating full dog image (complete dog body)")
            print("=" * 60)
            # Use the dog head image that was already generated to ensure consistency
            # Analyze both the original human image (for pose/position) and the dog head (for head characteristics)
            print("[METHOD 1] Analyzing images to create full dog with matching head...")
            
            # Get description of the human image for pose/position reference
            human_desc = analyze_image_characteristics(image_path)
            
            # Get description of the dog head for head characteristics
            dog_head_desc = None
            try:
                if os.path.exists(dog_path):
                    print("[METHOD 1] Analyzing generated dog head image...")
                    dog_head_desc = analyze_image_characteristics(dog_path)
            except Exception as e:
                print(f"[METHOD 1] Could not analyze dog head: {e}")
            
            if human_desc:
                print("[METHOD 1] Using image analysis with DALL-E 3...")
                
                # Build prompt that references the dog head but creates a complete dog body
                head_description = f" The dog's head should match the {breed} dog head characteristics from the generated dog head image" if dog_head_desc else f" The dog's head should be a {breed} dog head"
                
                prompt = f"""Photorealistic studio portrait of a complete {breed} dog with full body visible (all four legs, torso, tail, complete dog anatomy - NO human body visible).

Dog:
- Complete {breed} dog body with all four legs clearly visible
- Full dog torso, chest, and body (no human body parts)
- Dog head positioned in the same location and angle as the human head was in the original image
- {head_description}
- Dog's body positioned naturally - if the human was standing, the dog is standing on all four legs; if human was sitting, the dog is sitting naturally
- Natural, realistic {breed} dog anatomy and proportions throughout the entire body
- Dog's expression and gaze direction match the human's original expression from the original image
- The human has completely disappeared - only the dog remains

Background and Lighting:
- Professional studio portrait background (can be different from original, but should be appropriate for a dog portrait)
- Studio lighting appropriate for a dog portrait
- Same camera angle and framing as the original image (portrait orientation)
- The background can be different from the original image

Style:
- Ultra-realistic photography
- Shallow depth of field
- No illustration or cartoon
- High detail, natural dog pose
- Same camera angle and framing as original
- 85mm lens
- Realistic shadows
- Professional studio portrait quality
- The dog should look natural and complete, as if it was always a dog in this portrait"""
                
                result = generate_single_transformation_image(prompt, full_dog_path)
                if result:
                    print("✓ [SUCCESS] Full dog image generated using Image Analysis + DALL-E 3")
            else:
                # Fallback: simple prompt
                print("[METHOD 2] Image analysis failed, using simple fallback prompt...")
                prompt = f"""Photorealistic studio portrait of a complete {breed} dog with full body visible (all four legs, torso, tail - NO human body visible). The dog's head is positioned in the same location where a human head would be in a portrait photo. The dog has a complete, natural {breed} dog body - no human body parts. The human has completely disappeared. Professional studio portrait background (can be different from original). Natural, realistic {breed} dog anatomy throughout. Ultra-realistic photography style, shallow depth of field, high detail, professional studio portrait quality."""
                result = generate_single_transformation_image(prompt, full_dog_path)
                if result:
                    print("✓ [SUCCESS] Full dog image generated using Simple Fallback + DALL-E 3")
            results['full_dog'] = result
            if result:
                print("✓ Thread 2: Full dog image completed successfully")
            else:
                errors['full_dog'] = "Failed to generate full dog image"
                print("✗ Thread 2: Full dog image FAILED - all methods exhausted")
        except Exception as e:
            errors['full_dog'] = str(e)
            print(f"Thread 2: Error generating full dog image: {e}")
    
    def generate_final_img():
        """Generate final image (100% transformation - dog head fully integrated on human body)"""
        try:
            print("=" * 60)
            print("Thread 3: Generating final image (100% transformation - dog head on human body)")
            print("=" * 60)
            # Try GPT-Image-1 first
            print("[METHOD 1] Attempting GPT-Image-1 (direct image editing)...")
            result = edit_image_with_dog_head(image_path, dog_path, breed, final_path, transformation_level=1.0)
            if result:
                print("✓ [SUCCESS] Final image generated using GPT-Image-1")
            else:
                # Fall back to prompt-based generation using GPT-4 Vision
                print("[METHOD 2] GPT-Image-1 failed, trying GPT-4 Vision prompt generation...")
                prompt = create_composite_prompt_from_images(image_path, dog_path, breed, 1.0)
                if prompt:
                    print("[METHOD 2] Using GPT-4 Vision generated prompt with DALL-E 3...")
                    result = generate_single_transformation_image(prompt, final_path)
                    if result:
                        print("✓ [SUCCESS] Final image generated using GPT-4 Vision + DALL-E 3")
                else:
                    # If GPT-4 Vision refused, use analyze_image_characteristics as fallback
                    print("[METHOD 3] GPT-4 Vision refused, trying image analysis fallback...")
                    image_desc = analyze_image_characteristics(image_path)
                    if image_desc:
                        print("[METHOD 3] Using image analysis with DALL-E 3...")
                        prompt = f"""Photorealistic studio portrait.

Subject:
{image_desc}

Body:
- Human body with visible human shoulders, neck, and clothing
- Posture and clothing remain completely human and unchanged

Head:
- Realistic {breed} dog head
- Fully formed, expressive, and intelligent-looking
- Detailed {breed} characteristics and natural fur texture
- Natural neck anatomy
- Fur lighting matched to studio light
- Transition from dog head to human neck looks completely natural and anatomically correct

Style:
- Ultra-realistic photography
- Shallow depth of field
- No illustration or cartoon
- High detail, seamless anatomical integration
- 85mm lens
- Realistic shadows"""
                        result = generate_single_transformation_image(prompt, final_path)
                        if result:
                            print("✓ [SUCCESS] Final image generated using Image Analysis + DALL-E 3")
                    else:
                        # Final fallback: simple prompt without image analysis
                        print("[METHOD 4] Image analysis failed, using simple fallback prompt...")
                        prompt = f"""Photorealistic studio portrait of a {breed} dog head on a human body. The {breed} dog head is fully formed, expressive, and intelligent-looking with detailed {breed} characteristics and natural fur texture. The human body, clothing, pose, and background remain completely unchanged. Natural neck anatomy with seamless transition from dog head to human neck. Fur lighting matched to studio lighting. Ultra-realistic photography style, shallow depth of field, high detail, seamless anatomical integration."""
                        result = generate_single_transformation_image(prompt, final_path)
                        if result:
                            print("✓ [SUCCESS] Final image generated using Simple Fallback + DALL-E 3")
            results['final'] = result
            if result:
                print("✓ Thread 3: Final image completed successfully")
            else:
                errors['final'] = "Failed to generate final image"
                print("✗ Thread 3: Final image FAILED - all methods exhausted")
        except Exception as e:
            errors['final'] = str(e)
            print(f"Thread 3: Error generating final image: {e}")
    
    # Create threads for parallel generation
    print("Starting parallel image generation with 3 threads...")
    t1 = threading.Thread(target=generate_trans1)
    t2 = threading.Thread(target=generate_full_dog)
    t3 = threading.Thread(target=generate_final_img)
    
    # Start all threads
    t1.start()
    t2.start()
    t3.start()
    
    # Wait for all threads to complete
    t1.join()
    t2.join()
    t3.join()
    
    print("All image generation threads completed")
    
    # Check for errors
    if errors:
        print(f"Errors during generation: {errors}")
    
    # Return results (use paths even if generation failed, so caller can check file existence)
    # Note: Original image is unchanged and should be passed through separately
    return (
        results.get('trans1', trans1_path),  # Transition (30%)
        results.get('final', final_path),     # Final (100% - dog head on human body)
        results.get('full_dog', full_dog_path)  # Full dog (complete dog body)
    )
