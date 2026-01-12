# Shaggy Dog Transformer

Transform yourself into your perfect dog alter-ego using AI! Upload a photo and watch as AI creates a magical transformation through three stages, from human to your canine counterpart.

## Features

- 🔐 User authentication (register/login)
- 📸 Image upload and processing
- 🐕 AI-powered dog breed detection
- 🎨 Three-stage transformation visualization
- 📱 Responsive design
- 🚀 Ready for Render deployment

## Quick Start

### Prerequisites

- Python 3.8+
- Replicate API token ([Get one here](https://replicate.com))

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd shaggy-dog
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root:
   ```
   REPLICATE_API_TOKEN=your_replicate_api_token_here
   SECRET_KEY=your_secret_key_here
   ```
   
   Or set them in your environment:
   ```bash
   export REPLICATE_API_TOKEN=your_token
   export SECRET_KEY=your_secret_key
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Visit the app:**
   Open your browser and go to `http://localhost:5000`

## Project Structure

```
shaggy-dog/
├── app.py                 # Main Flask application
├── database.py            # Database operations
├── image_generator.py     # Replicate API integration
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── deployment.md         # Deployment instructions
├── static/
│   ├── style.css         # Stylesheet
│   └── script.js         # Frontend JavaScript
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── dashboard.html    # User dashboard
└── uploads/              # User uploaded images (created automatically)
```

## Usage

1. **Register an account** or **login** if you already have one
2. **Upload a photo** from your dashboard
3. **Wait for processing** - AI will analyze your photo and generate transformations
4. **View your transformations** - See the original, two transition stages, and final dog image

## Deployment

See [deployment.md](deployment.md) for detailed instructions on deploying to Render.

### Quick Deploy to Render

1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Deploy!

## Technology Stack

- **Backend:** Flask, Flask-Login
- **Database:** SQLite
- **AI/ML:** Replicate API (Flux model)
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render

## Notes

- The app uses Replicate's Flux model for image generation
- Images are stored locally in the `uploads/` directory
- On Render's free tier, files may be lost on restart (use cloud storage for production)
- First request after Render spin-down may take 30-60 seconds

## License

This project is for educational/demonstration purposes.

## Support

For issues or questions:
1. Check the deployment guide
2. Review application logs
3. Verify Replicate API token is valid
4. Ensure all dependencies are installed
