// Voice Recorder for Patient Form
// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingStartTime;
    let timerInterval;

    const recordButton = document.getElementById('recordButton');
    const recordButtonText = document.getElementById('recordButtonText');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingTimer = document.getElementById('recordingTimer');
    const recordingProgress = document.getElementById('recordingProgress');
    const transcriptionResult = document.getElementById('transcriptionResult');
    const transcriptionText = document.getElementById('transcriptionText');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Check if elements exist
    if (!recordButton) {
        console.error('Record button not found!');
        return;
    }

    console.log('Voice recorder initialized!');

    // Check browser support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        recordButton.disabled = true;
        recordButtonText.textContent = 'Браузер қўллаб-қувватламайди';
        console.error('MediaDevices API not supported');
        return;
    }

    recordButton.addEventListener('click', toggleRecording);

    async function toggleRecording() {
        console.log('Toggle recording clicked, isRecording:', isRecording);
        if (!isRecording) {
            await startRecording();
        } else {
            stopRecording();
        }
    }

    async function startRecording() {
        try {
            console.log('Starting recording...');
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('Microphone access granted');

            // Create MediaRecorder
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.addEventListener('dataavailable', event => {
                console.log('Data available, size:', event.data.size);
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', async () => {
                console.log('Recording stopped, chunks:', audioChunks.length);
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                console.log('Audio blob size:', audioBlob.size);
                await sendAudioForTranscription(audioBlob);

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            });

            mediaRecorder.start();
            isRecording = true;
            recordingStartTime = Date.now();

            // Update UI
            recordButton.classList.remove('btn-primary');
            recordButton.classList.add('btn', 'bg-red-600', 'hover:bg-red-700', 'text-white');
            recordButtonText.textContent = 'Ёзишни тўхтатиш';
            recordingStatus.classList.remove('hidden');
            transcriptionResult.classList.add('hidden');

            // Start timer
            updateTimer();
            timerInterval = setInterval(updateTimer, 1000);

            console.log('Recording started successfully');

        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Микрофонга кириш имкони йўқ. Илтимос, рухсат беринг.\n\nError: ' + error.message);
        }
    }

    function stopRecording() {
        console.log('Stopping recording...');
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;

            // Update UI
            recordButton.classList.remove('bg-red-600', 'hover:bg-red-700');
            recordButton.classList.add('btn-primary');
            recordButtonText.textContent = 'Ёзишни бошлаш';
            recordingStatus.classList.add('hidden');

            // Stop timer
            clearInterval(timerInterval);
        }
    }

    function updateTimer() {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        recordingTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        // Update progress bar (max 60 seconds)
        const progress = Math.min((elapsed / 60) * 100, 100);
        recordingProgress.style.width = `${progress}%`;
    }

    async function sendAudioForTranscription(audioBlob) {
        console.log('Sending audio for transcription...');
        // Show loading
        loadingIndicator.classList.remove('hidden');
        transcriptionResult.classList.add('hidden');

        try {
            // Create FormData
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            // Send to server
            const response = await fetch('/transcribe-audio/', {
                method: 'POST',
                body: formData
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                // Show transcription
                transcriptionText.textContent = data.transcription;
                transcriptionResult.classList.remove('hidden');

                // Show success message
                showMessage(data.message, 'success');
            } else {
                showMessage(data.message || 'Транскрипция қилишда хато', 'error');
            }

        } catch (error) {
            console.error('Error sending audio:', error);
            showMessage('Хато юз берди: ' + error.message, 'error');
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    }

    function showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-100 border-l-4 border-green-500 text-green-800' :
            'bg-red-100 border-l-4 border-red-500 text-red-800'
        }`;
        messageDiv.textContent = message;
        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
});
