document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const target = document.querySelector(tab.dataset.target);
            target.classList.add('active');

            // If switching to camera tab, start the camera
            if (tab.dataset.target === '#camera-tab') {
                // Small delay to allow DOM update
                setTimeout(startCamera, 50);
            } else {
                stopVideoStream();
            }
        });
    });

    // File input handling
    const fileInput = document.querySelector('.file-input');
    const fileName = document.querySelector('.file-name');

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            fileName.textContent = this.files[0].name;
            // Preview the selected image
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('preview').src = e.target.result;
                document.querySelector('.preview-wrapper').style.display = 'block';
            };
            reader.readAsDataURL(this.files[0]);
        } else {
            fileName.textContent = 'No file selected';
        }
    });

    // Camera functionality
    let stream = null;
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const startCameraBtn = document.getElementById('startCamera');
    const takePictureBtn = document.getElementById('takePicture');
    const retakePictureBtn = document.getElementById('retakePicture');

    // Start camera stream
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment' // Remove resolution constraints for compatibility
                } 
            });
            video.srcObject = stream;
            video.style.display = 'block';

            // Wait for video metadata to ensure valid dimensions
            await new Promise((resolve, reject) => {
                video.onloadedmetadata = () => {
                    video.play().then(resolve).catch(reject);
                };
            });

            startCameraBtn.style.display = 'none';
            takePictureBtn.style.display = 'inline-flex';
            document.querySelector('.preview-wrapper').style.display = 'none';
        } catch (err) {
            console.error('Camera Error:', err);
            let message = 'Error accessing camera. ';
            if (err.name === 'NotAllowedError') {
                message += 'Please check browser permissions.';
            } else {
                message += err.message;
            }
            alert(message);
        }
    }

    // Stop video stream
    function stopVideoStream() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            video.style.display = 'none';
            startCameraBtn.style.display = 'inline-flex';
            takePictureBtn.style.display = 'none';
        }
    }

    // Take picture from video stream
    function takePicture() {
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        // Convert canvas to blob
        canvas.toBlob(blob => {
            // Create a File object
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
            
            // Create a FileList-like object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            
            // Set the file input's files
            fileInput.files = dataTransfer.files;
            
            // Update preview
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('preview').src = e.target.result;
            };
            reader.readAsDataURL(file);
            
            // Show preview and retake button
            document.querySelector('.preview-wrapper').style.display = 'block';
            retakePictureBtn.style.display = 'inline-flex';
            
            // Hide video and take picture button
            video.style.display = 'none';
            takePictureBtn.style.display = 'none';
            
            // Stop the stream
            stopVideoStream();
        }, 'image/jpeg', 0.8);
    }

    // Event listeners for camera buttons
    startCameraBtn.addEventListener('click', startCamera);
    takePictureBtn.addEventListener('click', takePicture);
    retakePictureBtn.addEventListener('click', () => {
        document.querySelector('.preview-wrapper').style.display = 'none';
        retakePictureBtn.style.display = 'none';
        startCamera();
    });
}); 