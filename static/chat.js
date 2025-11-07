// WebSocket connection
let ws = null;
let isConnected = false;

// DOM elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const connectButton = document.getElementById('connectButton');

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
        connectButton.textContent = 'Disconnect';
        connectButton.style.background = '#dc3545';
    };
    
    ws.onclose = () => {
        isConnected = false;
        updateStatus(false);
        addSystemMessage('Disconnected from server.');
        messageInput.disabled = true;
        sendButton.disabled = true;
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

// Disconnect from WebSocket
function disconnect() {
    if (ws) {
        ws.close();
        ws = null;
    }
}

// Update connection status
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
    console.log('Received:', data);
    
    if (data.type === 'agent_response') {
        addAgentMessage(data.agent || 'Agent', data.message || data.content);
    } else if (data.type === 'code_result') {
        addAgentMessage('Code Executor', data.result, data.code);
    } else if (data.type === 'error') {
        addSystemMessage(`Error: ${data.message}`);
    } else if (data.type === 'status') {
        addSystemMessage(data.message);
    } else {
        // Generic response
        const message = data.message || data.content || JSON.stringify(data);
        addAgentMessage('Agent', message);
    }
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !isConnected) return;
    
    addUserMessage(message);
    
    // Send to server
    ws.send(JSON.stringify({
        type: 'user_message',
        message: message,
        timestamp: new Date().toISOString()
    }));
    
    messageInput.value = '';
}

// Add user message to chat
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add agent message to chat
function addAgentMessage(agent, text, code = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    
    const header = document.createElement('div');
    header.className = 'message-header';
    header.textContent = `${agent}:`;
    messageDiv.appendChild(header);
    
    const content = document.createElement('div');
    content.textContent = text;
    messageDiv.appendChild(content);
    
    if (code) {
        const codeBlock = document.createElement('div');
        codeBlock.className = 'code-block';
        const codeElement = document.createElement('code');
        codeElement.textContent = code;
        codeBlock.appendChild(codeElement);
        messageDiv.appendChild(codeBlock);
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add system message to chat
function addSystemMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Scroll to bottom of messages
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Event listeners
connectButton.addEventListener('click', () => {
    if (isConnected) {
        disconnect();
    } else {
        connect();
    }
});

sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Add some example suggestions
setTimeout(() => {
    addSystemMessage('💡 Try asking:');
    addSystemMessage('• "List files in the src directory"');
    addSystemMessage('• "What agents are available?"');
    addSystemMessage('• "Show me the main.py file"');
    addSystemMessage('• "Execute: print(2+2)"');
}, 1000);
