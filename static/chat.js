// WebSocket connection and Monaco editor + file explorer integration
let ws = null;
let isConnected = false;
let editor = null;
let currentFilePath = '';

// DOM elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const connectButton = document.getElementById('connectButton');
const fileListElem = document.getElementById('fileList');
const refreshFilesBtn = document.getElementById('refreshFiles');
const openButton = document.getElementById('openButton');
const saveButton = document.getElementById('saveButton');

// Utility: generate request id
function genId() { return Math.random().toString(36).slice(2, 10); }

// Initialize Monaco editor (via AMD loader)
function initMonaco() {
    require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@0.44.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        editor = monaco.editor.create(document.getElementById('editor'), {
            value: '// Open a file from the left file list to begin...',
            language: 'javascript',
            theme: 'vs-dark',
            automaticLayout: true,
        });
    });
}

// Connect to WebSocket
function connect() {
    const wsUrl = `ws://${window.location.hostname}:8000/ws`;
    addSystemMessage(`Connecting to ${wsUrl}...`);
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        isConnected = true;
        updateStatus(true);
        addSystemMessage('Connected! You can now chat with ADK agents.');
        messageInput.disabled = false;
        sendButton.disabled = false;
        openButton.disabled = false;
        saveButton.disabled = false;
        connectButton.textContent = 'Disconnect';
        connectButton.style.background = '#dc3545';
        // Request file list on connect
        listFiles('.');
    };

    ws.onclose = () => {
        isConnected = false;
        updateStatus(false);
        addSystemMessage('Disconnected from server.');
        messageInput.disabled = true;
        sendButton.disabled = true;
        openButton.disabled = true;
        saveButton.disabled = true;
        connectButton.textContent = 'Connect';
        connectButton.style.background = '#0e639c';
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addSystemMessage('Connection error. Make sure the backend is running on port 8000.');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleMessage(data);
        } catch (e) {
            console.error('Error parsing message:', e);
            addSystemMessage('Received invalid message from server.');
        }
    };
}

function disconnect() { if (ws) { ws.close(); ws = null; } }

function updateStatus(connected) {
    if (connected) {
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Handle incoming messages
function handleMessage(data) {
    // File explorer results
    if (data.type === 'file_explorer_result') {
        if (data.status === 'success' && data.data && data.data.items) {
            populateFileList(data.data.items);
            addSystemMessage(`Directory ${data.data.directory} — ${data.data.items.length} items`);
        } else if (data.status === 'success' && data.data && data.data.content) {
            // file read
            const content = data.data.content;
            const file_path = data.data.file_path || '';
            currentFilePath = file_path;
            if (editor) editor.setValue(content);
            addSystemMessage(`Opened ${file_path}`);
        } else {
            addSystemMessage(`File operation error: ${data.message || JSON.stringify(data)}`);
        }
        return;
    }

    if (data.type === 'agent_response') {
        addAgentMessage(data.agent || 'Agent', data.message || data.content);
        return;
    }

    if (data.type === 'terminal_result' || data.type === 'result') {
        addAgentMessage('Agent', JSON.stringify(data.data || data.result || data));
        return;
    }

    if (data.type === 'status' || data.type === 'ack' || data.type === 'progress') {
        addSystemMessage(data.message || JSON.stringify(data));
        return;
    }

    // Generic fallback
    addAgentMessage('Agent', JSON.stringify(data));
}

// Send a chat message to HIA via the websocket
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !isConnected) return;
    addUserMessage(message);
    ws.send(JSON.stringify({ type: 'user_message', message: message, timestamp: new Date().toISOString() }));
    messageInput.value = '';
}

// File operations: list, read, write
function listFiles(path) {
    if (!isConnected) return;
    const request = { type: 'file_explorer', request_id: genId(), payload: { action: 'list', path: path } };
    ws.send(JSON.stringify(request));
}

function openFile(path) {
    if (!isConnected) return;
    const request = { type: 'file_explorer', request_id: genId(), payload: { action: 'read', file_path: path } };
    ws.send(JSON.stringify(request));
}

function saveFile(path, content) {
    if (!isConnected) return;
    const request = { type: 'file_explorer', request_id: genId(), payload: { action: 'write', file_path: path, content: content } };
    ws.send(JSON.stringify(request));
}

// UI helpers
function populateFileList(items) {
    fileListElem.innerHTML = '';
    items.sort((a,b) => (a.type === b.type) ? a.name.localeCompare(b.name) : (a.type === 'directory' ? -1 : 1));
    items.forEach(it => {
        const li = document.createElement('li');
        li.className = 'agent-item';
        li.style.cursor = 'pointer';
        li.textContent = `${it.type === 'directory' ? '📁 ' : '📄 '}${it.name}`;
        li.addEventListener('click', () => {
            const fullPath = it.name;
            if (it.type === 'file') {
                openFile(fullPath);
            } else {
                // try listing subdirectory
                listFiles(fullPath);
            }
        });
        fileListElem.appendChild(li);
    });
}

function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addAgentMessage(agent, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    const header = document.createElement('div'); header.className = 'message-header'; header.textContent = `${agent}:`;
    messageDiv.appendChild(header);
    const content = document.createElement('div'); content.textContent = typeof text === 'string' ? text : JSON.stringify(text);
    messageDiv.appendChild(content);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addSystemMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function scrollToBottom() { messagesContainer.scrollTop = messagesContainer.scrollHeight; }

// Event listeners
connectButton.addEventListener('click', () => { if (isConnected) disconnect(); else connect(); });
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
refreshFilesBtn.addEventListener('click', () => listFiles('.'));
openButton.addEventListener('click', () => {
    const selection = Array.from(fileListElem.querySelectorAll('li.agent-item.selected')).map(n=>n.textContent).join(',');
    // open currently selected item if present; otherwise open currentFilePath
    if (currentFilePath) openFile(currentFilePath);
});
saveButton.addEventListener('click', () => {
    if (!currentFilePath) { addSystemMessage('No file opened to save'); return; }
    const content = editor ? editor.getValue() : '';
    saveFile(currentFilePath, content);
});

// Initial UI init
window.addEventListener('load', () => { initMonaco(); addSystemMessage('Editor initialized'); });

// Example hints
setTimeout(() => {
    addSystemMessage('💡 Try: Click Connect, click Refresh Files, open a file, edit and Save. Use the chat to ask agents about code.');
}, 800);
