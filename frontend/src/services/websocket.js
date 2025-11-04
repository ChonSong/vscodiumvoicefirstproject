class WebSocketConnection {
  constructor(callbacks = {}) {
    this.ws = null;
    this.callbacks = callbacks;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    
    this.connect();
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        if (this.callbacks.onConnect) {
          this.callbacks.onConnect();
        }
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (this.callbacks.onMessage) {
            this.callbacks.onMessage(message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (this.callbacks.onError) {
          this.callbacks.onError(error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        if (this.callbacks.onDisconnect) {
          this.callbacks.onDisconnect();
        }
        
        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
            console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            this.connect();
          }, this.reconnectDelay);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default WebSocketConnection;

