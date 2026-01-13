"""
Test script for OpenAI integration.
Tests breed analysis and image generation functionality.
"""
import os
import time
from dotenv import load_dotenv
import openai_generator

# Load environment variables
load_dotenv()

def clean_path(path):
    """Remove quotes and whitespace from path"""
    if not path:
        return ""
    # Strip whitespace and remove surrounding quotes
    path = path.strip()
    if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
        path = path[1:-1]
    return path

def test_analyze_dog_breed():
    """Test breed analysis with a sample image"""
    print("=" * 60)
    print("TEST 1: Testing breed analysis")
    print("=" * 60)
    
    # You'll need to provide a test image path
    # For example: "test_images/test_photo.jpg"
    test_image_path = clean_path(input("Enter path to test image (or press Enter to skip): "))
    
    if not test_image_path or not os.path.exists(test_image_path):
        print("Skipping breed analysis test - no valid image path provided")
        return None
    
    start_time = time.time()
    try:
        breed = openai_generator.analyze_dog_breed(test_image_path)
        elapsed = time.time() - start_time
        print(f"✓ Breed detected: {breed}")
        print(f"✓ Analysis took {elapsed:.2f} seconds")
        return breed
    except Exception as e:
        print(f"✗ Error during breed analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_generate_transformation_images():
    """Test image generation with a sample image and breed"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing image generation")
    print("=" * 60)
    
    # You'll need to provide a test image path
    test_image_path = clean_path(input("Enter path to test image (or press Enter to skip): "))
    
    if not test_image_path or not os.path.exists(test_image_path):
        print("Skipping image generation test - no valid image path provided")
        return
    
    # Get breed (or use a default)
    breed = input("Enter dog breed to use (or press Enter to analyze from image): ").strip()
    if not breed:
        print("Analyzing breed from image...")
        breed = openai_generator.analyze_dog_breed(test_image_path)
        if not breed:
            breed = "Golden Retriever"
            print(f"Using default breed: {breed}")
    
    print(f"Using breed: {breed}")
    
    # Generate test timestamp
    test_user_id = "test_user"
    test_timestamp = "test_" + str(int(time.time()))
    
    start_time = time.time()
    try:
        print("\nGenerating 3 transformation images in parallel...")
        trans1_path, final_path, full_dog_path = openai_generator.generate_transformation_images(
            test_image_path, breed, test_user_id, test_timestamp
        )
        elapsed = time.time() - start_time
        
        print(f"\n✓ Generation completed in {elapsed:.2f} seconds")
        print(f"\nResults:")
        print(f"  Original: {test_image_path}")
        print(f"    Exists: {os.path.exists(test_image_path) if test_image_path else False}")
        print(f"  Transition 1 (30%): {trans1_path}")
        print(f"    Exists: {os.path.exists(trans1_path) if trans1_path else False}")
        print(f"  Final (100% - dog head on human body): {final_path}")
        print(f"    Exists: {os.path.exists(final_path) if final_path else False}")
        print(f"  Full Dog (complete dog body): {full_dog_path}")
        print(f"    Exists: {os.path.exists(full_dog_path) if full_dog_path else False}")
        
        # Check file sizes
        if trans1_path and os.path.exists(trans1_path):
            size = os.path.getsize(trans1_path) / 1024
            print(f"    Size: {size:.2f} KB")
        if final_path and os.path.exists(final_path):
            size = os.path.getsize(final_path) / 1024
            print(f"    Size: {size:.2f} KB")
        if full_dog_path and os.path.exists(full_dog_path):
            size = os.path.getsize(full_dog_path) / 1024
            print(f"    Size: {size:.2f} KB")
            
    except Exception as e:
        print(f"✗ Error during image generation: {e}")
        import traceback
        traceback.print_exc()

def test_api_key():
    """Test if OpenAI API key is configured"""
    print("=" * 60)
    print("TEST 0: Checking OpenAI API key")
    print("=" * 60)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"✓ OpenAI API key found: {api_key[:10]}...{api_key[-4:]}")
        return True
    else:
        print("✗ OpenAI API key not found!")
        print("  Please set OPENAI_API_KEY in your .env file")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("OpenAI Integration Test Suite")
    print("=" * 60 + "\n")
    
    # Check API key first
    if not test_api_key():
        print("\n⚠ Cannot proceed without API key. Exiting.")
        exit(1)
    
    # Run tests
    breed = test_analyze_dog_breed()
    
    if breed:
        print(f"\nProceed with image generation using breed '{breed}'? (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            test_generate_transformation_images()
    else:
        print("\nProceed with image generation test anyway? (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            test_generate_transformation_images()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60 + "\n")
