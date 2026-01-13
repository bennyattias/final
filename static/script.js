// Form submission for image upload
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const imageGallery = document.getElementById('image-gallery');

    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Reset error message
            errorMessage.style.display = 'none';
            errorMessage.textContent = '';
            
            // Validate file selection
            if (!imageInput.files || imageInput.files.length === 0) {
                showError('Please select an image file');
                return;
            }
            
            const file = imageInput.files[0];
            
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                showError('Invalid file type. Please upload JPG, PNG, or GIF');
                return;
            }
            
            // Validate file size (10MB)
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                showError('File size too large. Please upload an image smaller than 10MB');
                return;
            }
            
            // Show loading spinner
            loadingSpinner.style.display = 'block';
            uploadForm.style.opacity = '0.5';
            uploadForm.style.pointerEvents = 'none';
            
            try {
                // Create FormData
                const formData = new FormData();
                formData.append('image', file);
                
                // Send POST request
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                // Check if response is JSON
                let data;
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    try {
                        data = await response.json();
                    } catch (e) {
                        // If JSON parsing fails, get text response
                        const text = await response.text();
                        throw new Error(`Server error: ${text || 'Invalid response'}`);
                    }
                } else {
                    // Not JSON, get text response
                    const text = await response.text();
                    throw new Error(`Server error: ${text || 'Invalid response format'}`);
                }
                
                if (!response.ok) {
                    throw new Error(data.error || 'Upload failed');
                }
                
                // Success - handle response
                if (data.success) {
                    if (data.status === 'processing') {
                        // Images are being generated in background - start polling
                        // Keep spinner visible while processing
                        loadingSpinner.querySelector('p').textContent = 'Transformations are being generated... This may take 1-2 minutes.';
                        startPolling(data.image_id, data.breed, data.images.original);
                    } else {
                        // All images ready - display immediately
                        displayNewImage(data);
                        // Hide loading spinner
                        loadingSpinner.style.display = 'none';
                        uploadForm.style.opacity = '1';
                        uploadForm.style.pointerEvents = 'auto';
                    }
                    // Reset form
                    uploadForm.reset();
                }
            
            } catch (error) {
                console.error('Upload error:', error);
                showError(error.message || 'An error occurred while uploading. Please try again.');
                // Hide loading spinner on error
                loadingSpinner.style.display = 'none';
                uploadForm.style.opacity = '1';
                uploadForm.style.pointerEvents = 'auto';
            } finally {
                // Only hide spinner if not processing (spinner stays visible during polling)
                if (!data || data.status !== 'processing') {
                    loadingSpinner.style.display = 'none';
                    uploadForm.style.opacity = '1';
                    uploadForm.style.pointerEvents = 'auto';
                }
            }
        });
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
    
    function displayNewImage(data) {
        // Only display if all 4 images are ready
        const images = data.images || {};
        if (!images.original || !images.transition1 || !images.final || !images.full_dog) {
            console.log('Waiting for all images to be generated...');
            return; // Don't display until all images are ready
        }
        
        // Create new image card
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card';
        
        const breed = data.breed || 'Unknown';
        
        // Display images in order 1->2->3->4 from left to right
        let imageStagesHTML = `
            <h4>Breed: ${breed}</h4>
            <div class="image-stages">
                <div class="image-stage">
                    <label>1. Original</label>
                    <img src="${images.original}" alt="Original">
                </div>
                <div class="image-stage">
                    <label>2. Transition</label>
                    <img src="${images.transition1}" alt="Transition">
                </div>
                <div class="image-stage">
                    <label>3. Final</label>
                    <img src="${images.final}" alt="Final">
                </div>
                <div class="image-stage">
                    <label>4. Full Dog</label>
                    <img src="${images.full_dog}" alt="Full Dog">
                </div>
            </div>
            <p class="image-date">Just now</p>
        `;
        
        imageCard.innerHTML = imageStagesHTML;
        
        // If gallery doesn't exist (no images yet), create it
        if (!imageGallery) {
            const gallerySection = document.querySelector('.gallery-section');
            if (gallerySection) {
                const newGallery = document.createElement('div');
                newGallery.className = 'image-gallery';
                newGallery.id = 'image-gallery';
                newGallery.appendChild(imageCard);
                gallerySection.appendChild(newGallery);
                
                // Remove "no images" message if it exists
                const noImages = gallerySection.querySelector('.no-images');
                if (noImages) {
                    noImages.remove();
                }
            }
        } else {
            // Prepend new image to gallery (most recent first)
            imageGallery.insertBefore(imageCard, imageGallery.firstChild);
        }
        
        // Scroll to new image
        imageCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Polling function to check if images are ready
    function startPolling(imageId, breed, originalUrl) {
        // Create a placeholder card showing "processing"
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card';
        imageCard.setAttribute('data-image-id', imageId);
        imageCard.innerHTML = `
            <h4>Breed: ${breed}</h4>
            <div class="image-stages">
                <div class="image-stage">
                    <label>1. Original</label>
                    <img src="${originalUrl}" alt="Original">
                </div>
                <div class="image-stage">
                    <label>2. Transition</label>
                    <div style="padding: 2rem; text-align: center; color: #999;">Processing...</div>
                </div>
                <div class="image-stage">
                    <label>3. Final</label>
                    <div style="padding: 2rem; text-align: center; color: #999;">Processing...</div>
                </div>
                <div class="image-stage">
                    <label>4. Full Dog</label>
                    <div style="padding: 2rem; text-align: center; color: #999;">Processing...</div>
                </div>
            </div>
            <p class="image-date">Just now - Processing...</p>
        `;
        
        // Add to gallery
        if (!imageGallery) {
            const gallerySection = document.querySelector('.gallery-section');
            if (gallerySection) {
                const newGallery = document.createElement('div');
                newGallery.className = 'image-gallery';
                newGallery.id = 'image-gallery';
                newGallery.appendChild(imageCard);
                gallerySection.appendChild(newGallery);
                
                const noImages = gallerySection.querySelector('.no-images');
                if (noImages) {
                    noImages.remove();
                }
            }
        } else {
            imageGallery.insertBefore(imageCard, imageGallery.firstChild);
        }
        
        // Scroll to new image
        imageCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Poll every 3 seconds
        let pollCount = 0;
        const maxPolls = 60; // 3 minutes max (60 * 3 seconds)
        
        const pollInterval = setInterval(async () => {
            pollCount++;
            
            try {
                const response = await fetch(`/check-status/${imageId}`);
                const statusData = await response.json();
                
                if (statusData.success && statusData.status === 'complete') {
                    // All images ready - update the card
                    clearInterval(pollInterval);
                    updateImageCard(imageId, statusData.images, breed);
                } else if (pollCount >= maxPolls) {
                    // Timeout - stop polling
                    clearInterval(pollInterval);
                    const card = document.querySelector(`[data-image-id="${imageId}"]`);
                    if (card) {
                        const dateEl = card.querySelector('.image-date');
                        if (dateEl) {
                            dateEl.textContent = 'Processing timeout - please refresh the page';
                            dateEl.style.color = '#e74c3c';
                        }
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
                if (pollCount >= maxPolls) {
                    clearInterval(pollInterval);
                }
            }
        }, 3000); // Poll every 3 seconds
    }
    
    function updateImageCard(imageId, images, breed) {
        const imageCard = document.querySelector(`[data-image-id="${imageId}"]`);
        if (!imageCard) return;
        
        imageCard.innerHTML = `
            <h4>Breed: ${breed}</h4>
            <div class="image-stages">
                <div class="image-stage">
                    <label>1. Original</label>
                    <img src="${images.original}" alt="Original">
                </div>
                <div class="image-stage">
                    <label>2. Transition</label>
                    <img src="${images.transition1}" alt="Transition">
                </div>
                <div class="image-stage">
                    <label>3. Final</label>
                    <img src="${images.final}" alt="Final">
                </div>
                <div class="image-stage">
                    <label>4. Full Dog</label>
                    <img src="${images.full_dog}" alt="Full Dog">
                </div>
            </div>
            <p class="image-date">Just now</p>
        `;
        
        // Hide loading spinner now that images are ready
        const loadingSpinner = document.getElementById('loading-spinner');
        const uploadForm = document.getElementById('upload-form');
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        if (uploadForm) {
            uploadForm.style.opacity = '1';
            uploadForm.style.pointerEvents = 'auto';
        }
    }
});
