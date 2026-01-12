"""
Simple test script for Shaggy Dog application
Tests basic functionality without requiring Replicate API calls
"""

import os
import sys
import database

def test_database():
    """Test database operations"""
    print("Testing database operations...")
    
    # Initialize database
    try:
        database.init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[FAIL] Database initialization failed: {e}")
        return False
    
    # Test user creation
    test_username = "test_user_" + str(os.getpid())
    test_password = "test_password_123"
    
    try:
        user_id = database.create_user(test_username, test_password)
        if user_id:
            print(f"[OK] User created with ID: {user_id}")
        else:
            print("[FAIL] User creation returned None (user may already exist)")
    except Exception as e:
        print(f"[FAIL] User creation failed: {e}")
        return False
    
    # Test user verification
    try:
        user_data = database.verify_user(test_username, test_password)
        if user_data and user_data['username'] == test_username:
            print("[OK] User verification successful")
        else:
            print("[FAIL] User verification failed")
            return False
    except Exception as e:
        print(f"[FAIL] User verification failed: {e}")
        return False
    
    # Test wrong password
    try:
        user_data = database.verify_user(test_username, "wrong_password")
        if user_data is None:
            print("[OK] Wrong password correctly rejected")
        else:
            print("[FAIL] Wrong password was accepted (security issue!)")
            return False
    except Exception as e:
        print(f"[FAIL] Password verification test failed: {e}")
        return False
    
    # Test get user by ID
    try:
        user_data = database.get_user_by_id(user_id)
        if user_data and user_data['id'] == user_id:
            print("[OK] Get user by ID successful")
        else:
            print("[FAIL] Get user by ID failed")
            return False
    except Exception as e:
        print(f"[FAIL] Get user by ID failed: {e}")
        return False
    
    # Test image set saving
    try:
        image_id = database.save_image_set(
            user_id,
            "test_original.jpg",
            "Golden Retriever",
            "test_trans1.png",
            "test_trans2.png",
            "test_final.png"
        )
        if image_id:
            print(f"[OK] Image set saved with ID: {image_id}")
        else:
            print("[FAIL] Image set saving failed")
            return False
    except Exception as e:
        print(f"[FAIL] Image set saving failed: {e}")
        return False
    
    # Test get user images
    try:
        images = database.get_user_images(user_id)
        if images and len(images) > 0:
            print(f"[OK] Retrieved {len(images)} image(s) for user")
        else:
            print("[FAIL] No images retrieved")
            return False
    except Exception as e:
        print(f"[FAIL] Get user images failed: {e}")
        return False
    
    print("\n[OK] All database tests passed!")
    return True

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("[OK] Flask imported")
    except ImportError as e:
        print(f"[FAIL] Flask import failed: {e}")
        return False
    
    try:
        from flask_login import LoginManager
        print("[OK] Flask-Login imported")
    except ImportError as e:
        print(f"[FAIL] Flask-Login import failed: {e}")
        return False
    
    try:
        from werkzeug.security import generate_password_hash
        print("[OK] Werkzeug imported")
    except ImportError as e:
        print(f"[FAIL] Werkzeug import failed: {e}")
        return False
    
    try:
        import replicate
        print("[OK] Replicate imported")
    except (ImportError, Exception) as e:
        print(f"[WARN] Replicate import failed: {e}")
        print("  Note: Replicate is optional for basic tests")
        print("  This may be a compatibility issue - app should still work")
    
    try:
        from PIL import Image
        print("[OK] Pillow imported")
    except ImportError as e:
        print(f"[FAIL] Pillow import failed: {e}")
        return False
    
    print("\n[OK] All imports successful!")
    return True

def test_file_structure():
    """Test that required files and directories exist"""
    print("Testing file structure...")
    
    required_files = [
        'app.py',
        'database.py',
        'image_generator.py',
        'requirements.txt',
        'static/style.css',
        'static/script.js',
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/dashboard.html'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path} exists")
        else:
            print(f"[FAIL] {file_path} missing")
            all_exist = False
    
    # Check uploads directory
    if os.path.exists('uploads'):
        print("[OK] uploads/ directory exists")
    else:
        print("[WARN] uploads/ directory missing (will be created on first run)")
    
    if all_exist:
        print("\n[OK] All required files present!")
    else:
        print("\n[FAIL] Some files are missing!")
    
    return all_exist

def main():
    """Run all tests"""
    print("=" * 50)
    print("Shaggy Dog Application - Test Suite")
    print("=" * 50)
    print()
    
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
