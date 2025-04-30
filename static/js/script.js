function displayRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        
        const icon = document.createElement('div');
        icon.className = 'recommendation-icon';
        icon.innerHTML = rec.icon || '💡';
        
        const text = document.createElement('div');
        text.className = 'recommendation-text';
        text.textContent = rec.text;
        
        item.appendChild(icon);
        item.appendChild(text);
        recommendationsList.appendChild(item);
    });
}

function displayResult(result) {
    const resultText = document.getElementById('resultText');
    const recommendations = document.getElementById('recommendations');
    
    resultText.textContent = result.text;
    if (result.recommendations) {
        displayRecommendations(result.recommendations);
        recommendations.style.display = 'block';
    } else {
        recommendations.style.display = 'none';
    }
}

// DOM Elements
const fileTab = document.getElementById('fileTab');
const cameraTab = document.getElementById('cameraTab');
const fileContent = document.getElementById('fileContent');
const cameraContent = document.getElementById('cameraContent');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const video = document.getElementById('video');
const preview = document.getElementById('preview');
const startCameraBtn = document.getElementById('startCamera');
const takePictureBtn = document.getElementById('takePicture');
const retakePictureBtn = document.getElementById('retakePicture');
const scanForm = document.getElementById('scanForm');

let stream = null;

// Tab switching functionality
fileTab.addEventListener('click', () => {
    fileTab.classList.add('active');
    cameraTab.classList.remove('active');
    fileContent.classList.add('active');
    cameraContent.classList.remove('active');
    stopCamera();
});

cameraTab.addEventListener('click', () => {
    cameraTab.classList.add('active');
    fileTab.classList.remove('active');
    cameraContent.classList.add('active');
    fileContent.classList.remove('active');
});

// File input handling
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileName.textContent = e.target.files[0].name;
    } else {
        fileName.textContent = 'No file selected';
    }
});

// Camera functionality
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment'
            }
        });
        video.srcObject = stream;
        video.style.display = 'block';
        preview.style.display = 'none';
        startCameraBtn.style.display = 'none';
        takePictureBtn.style.display = 'inline-block';
        retakePictureBtn.style.display = 'none';
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert('Error accessing camera. Please make sure you have granted camera permissions.');
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    video.srcObject = null;
}

function takePicture() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    preview.src = canvas.toDataURL('image/jpeg');
    preview.style.display = 'block';
    video.style.display = 'none';
    takePictureBtn.style.display = 'none';
    retakePictureBtn.style.display = 'inline-block';
    
    // Create a blob from the canvas data
    canvas.toBlob((blob) => {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        fileName.textContent = 'camera-capture.jpg';
    }, 'image/jpeg');
}

function retakePicture() {
    video.style.display = 'block';
    preview.style.display = 'none';
    takePictureBtn.style.display = 'inline-block';
    retakePictureBtn.style.display = 'none';
    fileInput.value = '';
    fileName.textContent = 'No file selected';
}

// Event listeners for camera controls
startCameraBtn.addEventListener('click', startCamera);
takePictureBtn.addEventListener('click', takePicture);
retakePictureBtn.addEventListener('click', retakePicture);

// Form submission
scanForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(scanForm);
    
    try {
        const response = await fetch('/scan', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Update results
        const resultBlock = document.getElementById('result-block');
        resultBlock.innerHTML = `
            <h2>Scan Results</h2>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;
        
        // Update recommendations if available
        if (data.recommendations) {
            const recommendationsList = document.getElementById('recommendationsList');
            recommendationsList.innerHTML = data.recommendations
                .map(rec => `<div class="recommendation-item">${rec}</div>`)
                .join('');
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing the receipt. Please try again.');
    }
});

// Initialize UI
takePictureBtn.style.display = 'none';
retakePictureBtn.style.display = 'none';
preview.style.display = 'none'; 