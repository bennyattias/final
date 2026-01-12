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
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Upload failed');
                }
                
                // Success - display new images
                if (data.success) {
                    displayNewImage(data);
                    // Reset form
                    uploadForm.reset();
                }
                
            } catch (error) {
                console.error('Upload error:', error);
                showError(error.message || 'An error occurred while uploading. Please try again.');
            } finally {
                // Hide loading spinner
                loadingSpinner.style.display = 'none';
                uploadForm.style.opacity = '1';
                uploadForm.style.pointerEvents = 'auto';
            }
        });
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
    
    function displayNewImage(data) {
        // Create new image card
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card';
        
        const breed = data.breed || 'Unknown';
        const images = data.images || {};
        
        let imageStagesHTML = `
            <h4>Breed: ${breed}</h4>
            <div class="image-stages">
                <div class="image-stage">
                    <label>Original</label>
                    <img src="${images.original || ''}" alt="Original" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ddd\' width=\'200\' height=\'200\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3ELoading...%3C/text%3E%3C/svg%3E'">
                </div>
        `;
        
        if (images.transition1) {
            imageStagesHTML += `
                <div class="image-stage">
                    <label>Transition 1</label>
                    <img src="${images.transition1}" alt="Transition 1" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ddd\' width=\'200\' height=\'200\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3ELoading...%3C/text%3E%3C/svg%3E'">
                </div>
            `;
        }
        
        if (images.transition2) {
            imageStagesHTML += `
                <div class="image-stage">
                    <label>Transition 2</label>
                    <img src="${images.transition2}" alt="Transition 2" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ddd\' width=\'200\' height=\'200\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3ELoading...%3C/text%3E%3C/svg%3E'">
                </div>
            `;
        }
        
        if (images.final) {
            imageStagesHTML += `
                <div class="image-stage">
                    <label>Final Dog</label>
                    <img src="${images.final}" alt="Final Dog" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ddd\' width=\'200\' height=\'200\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3ELoading...%3C/text%3E%3C/svg%3E'">
                </div>
            `;
        }
        
        imageStagesHTML += `
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
    
    // Progressive image loading for transition images
    // This function can be called as images are generated
    function updateImageProgress(imageId, stage, imageUrl) {
        const imageCard = document.querySelector(`[data-image-id="${imageId}"]`);
        if (imageCard) {
            const stageElement = imageCard.querySelector(`[data-stage="${stage}"]`);
            if (stageElement) {
                const img = stageElement.querySelector('img');
                if (img) {
                    img.src = imageUrl;
                }
            }
        }
    }
});
