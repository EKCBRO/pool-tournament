// Registration form handler
const form = document.getElementById('registrationForm');
const photoInput = document.getElementById('playerPhoto');
const photoPreview = document.getElementById('photoPreview');
const fileName = document.getElementById('fileName');
const nameInput = document.getElementById('playerName');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');

let cameraStream = null;
let capturedPhotoData = null;

// Camera functions
async function openCamera() {
    const cameraView = document.getElementById('cameraView');
    const video = document.getElementById('cameraVideo');
    
    try {
        // Request camera access (prefer front camera)
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'user' },
            audio: false 
        });
        
        video.srcObject = cameraStream;
        cameraView.style.display = 'block';
        fileName.textContent = 'Camera active';
    } catch (error) {
        console.error('Camera error:', error);
        showError('Unable to access camera. Please check permissions or use file upload.');
    }
}

function closeCamera() {
    const cameraView = document.getElementById('cameraView');
    const video = document.getElementById('cameraVideo');
    
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    video.srcObject = null;
    cameraView.style.display = 'none';
    
    if (!capturedPhotoData && !photoInput.files[0]) {
        fileName.textContent = 'No file chosen';
    }
}

function capturePhoto() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.createElement('canvas');
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convert to data URL
    capturedPhotoData = canvas.toDataURL('image/jpeg', 0.9);
    
    // Update preview
    photoPreview.innerHTML = `<img src="${capturedPhotoData}" alt="Preview">`;
    fileName.textContent = 'Photo captured from camera';
    
    // Clear file input since we're using camera
    photoInput.value = '';
    
    // Close camera
    closeCamera();
}

window.openCamera = openCamera;
window.closeCamera = closeCamera;
window.capturePhoto = capturePhoto;

// Preview photo when selected
photoInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    
    // Clear captured photo if switching to file upload
    capturedPhotoData = null;
    
    if (file) {
        // Update file name display
        fileName.textContent = file.name;
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showError('Photo size must be less than 5MB');
            photoInput.value = '';
            fileName.textContent = 'No file chosen';
            return;
        }
        
        // Check file type
        if (!file.type.startsWith('image/')) {
            showError('Please select a valid image file');
            photoInput.value = '';
            fileName.textContent = 'No file chosen';
            return;
        }
        
        // Preview the image
        const reader = new FileReader();
        reader.onload = function(event) {
            photoPreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    } else {
        fileName.textContent = 'No file chosen';
        photoPreview.innerHTML = '<div style="color: #FFD700;">No photo selected</div>';
    }
});

// Handle form submission
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const playerName = nameInput.value.trim();
    const photoFile = photoInput.files[0];
    
    if (!playerName) {
        showError('Please enter your name');
        return;
    }
    
    // Check if we have either a captured photo or uploaded file
    if (!capturedPhotoData && !photoFile) {
        showError('Please take a photo or upload a file');
        return;
    }
    
    // If we have captured photo, use it directly
    if (capturedPhotoData) {
        savePlayer(playerName, capturedPhotoData);
        return;
    }
    
    // Otherwise, convert uploaded file to base64
    const reader = new FileReader();
    reader.onload = async function(event) {
        const imageData = event.target.result;
        savePlayer(playerName, imageData);
    };
    reader.readAsDataURL(photoFile);
});

async function savePlayer(playerName, imageData) {
    try {
        // Send player data to server
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: playerName,
                photo: imageData
            })
        });
        
        if (!response.ok) {
            throw new Error('Registration failed');
        }
        
        const result = await response.json();
        
        // Show success message
        showSuccess();
        
        // Redirect after 2 seconds
        setTimeout(() => {
            window.location.href = 'matchup.html';
        }, 2000);
    } catch (error) {
        console.error('Error:', error);
        showError('Error saving player data. Please try again.');
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
    
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function showSuccess() {
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
    form.style.opacity = '0.5';
    form.style.pointerEvents = 'none';
}

// Auto-capitalize first letters of each word
nameInput.addEventListener('input', function(e) {
    const words = this.value.split(' ');
    const capitalized = words.map(word => {
        if (word.length > 0) {
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        }
        return word;
    });
    
    const cursorPos = this.selectionStart;
    this.value = capitalized.join(' ');
    this.setSelectionRange(cursorPos, cursorPos);
});

// Clean up camera on page unload
window.addEventListener('beforeunload', () => {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
    }
});
