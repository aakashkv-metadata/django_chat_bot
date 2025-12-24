document.addEventListener('DOMContentLoaded', () => {
    // --- File Upload Logic ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseLink = document.getElementById('browse-link');
    const uploadStatus = document.getElementById('upload-status');
    const chatInput = document.getElementById('user-input');

    // Trigger file input
    browseLink.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & Drop visual feedback
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    // Handle Drop
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle Input Change
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }

    function uploadFile(file) {
        if (file.type !== 'application/pdf') {
            showStatus('Please upload a PDF file.', 'error');
            return;
        }

        showStatus(`Uploading ${file.name}...`, 'loading');

        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/upload/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showStatus('File uploaded and processed successfully!', 'success');
                chatInput.focus();
            } else {
                showStatus('Upload failed: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showStatus('An error occurred during upload.', 'error');
            console.error('Error:', error);
        });
    }

    function showStatus(msg, type) {
        uploadStatus.textContent = msg;
        uploadStatus.className = `status-msg ${type}`;
    }

    // --- Chat Logic ---
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function sendMessage() {
        const query = userInput.value.trim();
        if (!query) return;

        // Add user message
        appendMessage('user', query);
        userInput.value = '';

        // Add loading placeholder
        const loadingId = appendMessage('ai', 'Thinking...');

        // Call API
        fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            removeMessage(loadingId);
            if (data.answer) {
                appendMessage('ai', data.answer);
            } else {
                appendMessage('ai', 'Sorry, something went wrong: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            removeMessage(loadingId);
            appendMessage('ai', 'Error connecting to server.');
            console.error('Error:', error);
        });
    }

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        const id = 'msg-' + Date.now();
        msgDiv.id = id;

        // Avatar
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        if (sender === 'ai') {
            avatar.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2" /><circle cx="12" cy="5" r="2" /><path d="M12 7v4" /><line x1="8" y1="16" x2="8" y2="16" /><line x1="16" y1="16" x2="16" y2="16" /></svg>`;
        } else {
            // User avatar (empty/hidden by CSS or icon)
            avatar.innerHTML = `<span>U</span>`; 
        }

        // Content
        const content = document.createElement('div');
        content.className = 'content';
        
        // Parse Markdown if AI
        if (sender === 'ai' && typeof marked !== 'undefined') {
            content.innerHTML = marked.parse(text);
        } else {
            content.textContent = text;
        }

        if(sender === 'ai') msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);
        if(sender === 'user') msgDiv.appendChild(avatar);

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
