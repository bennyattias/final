import os
import openai
import replicate
import threading
from PIL import Image, ImageDraw, ImageFilter
import time
import urllib.request
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key from environment
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    print(f"OpenAI API key loaded: {OPENAI_API_KEY[:10]}...")
else:
    print("WARNING: OPENAI_API_KEY not found in environment!")

# Load Replicate API token from environment
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
if REPLICATE_API_TOKEN:
    os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN
    print(f"Replicate API token loaded: {REPLICATE_API_TOKEN[:10]}...")
else:
    print("WARNING: REPLICATE_API_TOKEN not found in environment!")

def analyze_dog_breed(image_path):
    """
    Analyze the uploaded image to determine the closest dog breed.
    Uses OpenAI's GPT-4 Vision to analyze facial features.
    """
    try:
        if not OPENAI_API_KEY:
            print("OpenAI API key not found, using default breed")
            return "Golden Retriever"
        
        # Read the image and encode it
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Use GPT-4 Vision to analyze the image
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Determine image MIME type
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png" if ext == '.png' else "image/jpeg"
        
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-vision-preview" if gpt-4o doesn't work
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Look at this portrait photo and suggest which dog breed would be a good match based on facial features and characteristics. Return only the dog breed name, nothing else. Examples: Golden Retriever, German Shepherd, Bulldog, Beagle, Poodle."
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

def generate_single_image(prompt, output_path, image_path=None):
    """Generate a single image using OpenAI DALL-E 3"""
    try:
        # Check if OpenAI API key is set
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY not set in environment")
            return None
        
        print(f"Generating image with prompt: {prompt[:50]}...")
        
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
            urllib.request.urlretrieve(image_url, output_path)
            print(f"Image saved to: {output_path}")
            return output_path
        else:
            print("ERROR: No image URL returned from OpenAI")
            return None
            
    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_dog_image(breed, user_image_path, output_path):
    """Generate a dog image based on the breed that resembles the user"""
    # First, get a description of the user's features to make the dog similar
    try:
        if OPENAI_API_KEY:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Read the user image
            with open(user_image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            ext = os.path.splitext(user_image_path)[1].lower()
            mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png" if ext == '.png' else "image/jpeg"
            
            # Get description of user's facial features
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe the key facial features of this person in 2-3 short phrases. Focus on: face shape (round, oval, square, etc.), eye characteristics (size, shape, expression), hair characteristics (color, texture, style), and overall expression/personality. Keep it brief - just the essential features."
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
                max_tokens=100
            )
            
            user_features = response.choices[0].message.content.strip()
            print(f"User features: {user_features}")
            
            # Check if GPT-4 refused
            if "sorry" in user_features.lower() or "can't" in user_features.lower() or "cannot" in user_features.lower():
                print("GPT-4 refused to describe features, using default prompt")
                prompt = f"A beautiful photorealistic portrait of a {breed} dog with expressive eyes, looking directly at the camera. Professional pet photography, studio lighting, high quality, detailed, realistic, adorable {breed} dog portrait, headshot, clear background."
            else:
                # Create a prompt that incorporates user features
                prompt = f"A photorealistic portrait of a {breed} dog that captures similar characteristics to a person with {user_features}. The dog should have a similar expression, eye characteristics, and overall vibe. Professional pet photography, studio lighting, high quality, detailed, realistic {breed} dog portrait, headshot, looking directly at camera."
        else:
            # Fallback prompt without user features
            prompt = f"A beautiful photorealistic portrait of a {breed} dog with expressive eyes, looking directly at the camera. Professional pet photography, studio lighting, high quality, detailed, realistic, adorable {breed} dog portrait, headshot, clear background."
    except Exception as e:
        print(f"Error getting user features, using default prompt: {e}")
        prompt = f"A beautiful photorealistic portrait of a {breed} dog with expressive eyes, looking directly at the camera. Professional pet photography, studio lighting, high quality, detailed, realistic, adorable {breed} dog portrait, headshot, clear background."
    
    return generate_single_image(prompt, output_path)

def blend_faces_manually(source_image_path, target_image_path, output_path, blend_factor=0.5):
    """
    Manually blend the dog face into the human image using PIL.
    blend_factor: 0.0 = all human, 1.0 = all dog, 0.5 = 50/50
    """
    try:
        from PIL import Image, ImageFilter, ImageDraw
        
        # Open both images
        human_img = Image.open(target_image_path).convert('RGBA')
        dog_img = Image.open(source_image_path).convert('RGBA')
        
        # Resize dog image to match human image
        dog_img = dog_img.resize(human_img.size, Image.Resampling.LANCZOS)
        
        # Estimate face region (upper center portion)
        width, height = human_img.size
        face_width = int(width * 0.6)
        face_height = int(height * 0.4)
        face_x = (width - face_width) // 2
        face_y = int(height * 0.1)
        
        # Create a mask for the face region with feathered edges
        mask = Image.new('L', human_img.size, 0)
        draw = ImageDraw.Draw(mask)
        padding = int(min(face_width, face_height) * 0.1)
        draw.ellipse(
            [face_x - padding, face_y - padding, face_x + face_width + padding, face_y + face_height + padding],
            fill=255
        )
        mask = mask.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Blend only the face region
        # Create a copy of human image
        result = human_img.copy()
        
        # Extract face regions
        human_face = human_img.crop((face_x, face_y, face_x + face_width, face_y + face_height))
        dog_face = dog_img.crop((face_x, face_y, face_x + face_width, face_y + face_height))
        
        # Blend the faces
        blended_face = Image.blend(human_face, dog_face, blend_factor)
        
        # Create temp image with blended face
        temp_img = Image.new('RGBA', human_img.size, (0, 0, 0, 0))
        temp_img.paste(blended_face, (face_x, face_y))
        
        # Composite using the mask
        result = Image.composite(temp_img, result, mask)
        
        # Save
        if output_path.endswith('.png'):
            result = result.convert('RGBA')
            result.save(output_path, 'PNG')
        else:
            result = result.convert('RGB')
            result.save(output_path, 'JPEG', quality=95)
        
        print(f"Blended face saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error blending faces: {e}")
        import traceback
        traceback.print_exc()
        return None

def swap_face_using_replicate(source_image_path, target_image_path, output_path):
    """
    Use Replicate's face swap model to swap the dog face into the human image.
    source_image_path: The dog image (source face)
    target_image_path: The human image (target - where face will be swapped)
    output_path: Where to save the result
    """
    try:
        if not REPLICATE_API_TOKEN:
            print("ERROR: REPLICATE_API_TOKEN not set in environment")
            return None
        
        print(f"Fully swapping face using Replicate...")
        print(f"Source (dog): {source_image_path}")
        print(f"Target (human): {target_image_path}")
        
        # Open the images as file objects
        # The model expects: input_image (target/human) and swap_image (source/dog)
        with open(target_image_path, 'rb') as input_file, open(source_image_path, 'rb') as swap_file:
            # Use the specified face swap model
            model_name = "cdingram/face-swap:d1d6ea8c8be89d664a07a457526f7128109dee7030fdac424788d762c71ed111"
            print(f"Using face swap model: {model_name}")
            
            output = replicate.run(
                model_name,
                input={
                    "input_image": input_file,  # The human image (where face will be swapped)
                    "swap_image": swap_file     # The dog image (face to swap in)
                }
            )
        
        # Download the result
        if output:
            image_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else str(output))
            if image_url:
                print(f"Downloading swapped face image from: {image_url}")
                urllib.request.urlretrieve(image_url, output_path)
                print(f"Face swap saved to: {output_path}")
                return output_path
        
        return None
        
    except Exception as e:
        print(f"Error swapping face with Replicate: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_transition1(image_path, breed, dog_image_path, output_path):
    """Generate transition 1: 30% dog, 70% human (blended)"""
    return blend_faces_manually(dog_image_path, image_path, output_path, blend_factor=0.3)

def generate_transition2(image_path, breed, dog_image_path, output_path):
    """Generate transition 2: 70% dog, 30% human (blended)"""
    return blend_faces_manually(dog_image_path, image_path, output_path, blend_factor=0.7)

def generate_final(image_path, breed, dog_image_path, output_path):
    """Generate final image: 100% dog face (full replacement using Replicate)"""
    return swap_face_using_replicate(dog_image_path, image_path, output_path)

def generate_transformation_images(image_path, breed, user_id, timestamp):
    """
    Generate transformation images:
    1. Generate a dog image based on the breed
    2. Composite the dog into the user's image at different blend levels
    Returns paths to all generated images.
    """
    base_path = f"uploads/{user_id}_{timestamp}"
    
    dog_image_path = f"{base_path}_dog.png"
    trans1_path = f"{base_path}_transition1.png"
    trans2_path = f"{base_path}_transition2.png"
    final_path = f"{base_path}_final.png"
    
    print(f"Step 1: Generating {breed} dog image that resembles the user...")
    # First, generate the dog image (pass user image so it can be similar)
    dog_path = generate_dog_image(breed, image_path, dog_image_path)
    
    if not dog_path:
        print("ERROR: Failed to generate dog image")
        return (None, None, None)
    
    print(f"Step 2: Dog image generated. Now compositing into user image...")
    
    # Now composite the dog into the user's image at different blend levels
    results = {}
    errors = {}
    
    def generate_trans1():
        try:
            results['trans1'] = generate_transition1(image_path, breed, dog_path, trans1_path)
        except Exception as e:
            errors['trans1'] = str(e)
            print(f"Error in transition 1: {e}")
    
    def generate_trans2():
        try:
            results['trans2'] = generate_transition2(image_path, breed, dog_path, trans2_path)
        except Exception as e:
            errors['trans2'] = str(e)
            print(f"Error in transition 2: {e}")
    
    def generate_final_img():
        try:
            results['final'] = generate_final(image_path, breed, dog_path, final_path)
        except Exception as e:
            errors['final'] = str(e)
            print(f"Error in final image: {e}")
    
    # Generate composited images sequentially (faster than threading for image processing)
    print("Generating transition 1 (30% dog)...")
    generate_trans1()
    
    print("Generating transition 2 (70% dog)...")
    generate_trans2()
    
    print("Generating final image (95% dog)...")
    generate_final_img()
    
    # Check for errors
    if errors:
        print(f"Errors during generation: {errors}")
    
    return (
        results.get('trans1', trans1_path),
        results.get('trans2', trans2_path),
        results.get('final', final_path)
    )
