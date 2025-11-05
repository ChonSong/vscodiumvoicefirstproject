import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid } from '@mui/material';
import CodeEditor from './components/CodeEditor';
import AgentStatus from './components/AgentStatus';
import ChatInterface from './components/ChatInterface';
import FileExplorer from './components/FileExplorer';
import EmbeddedTerminal from './components/EmbeddedTerminal';
import WebSocketConnection from './services/websocket';

function App() {
  const [wsConnected, setWsConnected] = useState(false);
  const [agentStatus] = useState({});
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const ws = new WebSocketConnection({
      onConnect: () => setWsConnected(true),
      onDisconnect: () => setWsConnected(false),
      onMessage: (message) => {
        if (message.type === 'progress') {
          setMessages(prev => [...prev, { type: 'info', text: message.message }]);
        } else if (message.type === 'result') {
          setMessages(prev => [...prev, { type: 'success', text: JSON.stringify(message.data, null, 2) }]);
        } else if (message.type === 'error') {
          setMessages(prev => [...prev, { type: 'error', text: message.message }]);
        }
      },
    });

    return () => ws.disconnect();
  }, []);

  const handleCodeExecute = async (code) => {
    const ws = new WebSocketConnection();
    ws.send({
      type: 'execute_code',
      request_id: Date.now().toString(),
      payload: { code },
    });
  };

  const handleAgentRequest = async (request) => {
    const ws = new WebSocketConnection();
    ws.send({
      type: 'orchestrate',
      request_id: Date.now().toString(),
      payload: request,
    });
  };

  const handleFileSelect = (filePath) => {
    // TODO: Load file content into CodeEditor when file loading is implemented
    console.log('Selected file:', filePath);
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#1e1e1e' }}>
      <Box sx={{ bgcolor: '#252526', p: 2, borderBottom: '1px solid #3e3e42' }}>
        <Typography variant="h5" sx={{ color: '#cccccc', fontWeight: 'bold' }}>
          ADK IDE
        </Typography>
        <Typography variant="caption" sx={{ color: wsConnected ? '#4ec9b0' : '#f48771' }}>
          {wsConnected ? 'Connected' : 'Disconnected'}
        </Typography>
      </Box>
      
      <Grid container sx={{ flex: 1, overflow: 'hidden' }}>
        {/* Left Sidebar - File Explorer */}
        <Grid item xs={2} sx={{ borderRight: '1px solid #3e3e42', overflow: 'hidden' }}>
          <FileExplorer onFileSelect={handleFileSelect} />
        </Grid>
        
        {/* Main Content Area */}
        <Grid item xs={7} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ flex: 1, p: 2, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flex: 1, mb: 2, minHeight: 0 }}>
              <CodeEditor onExecute={handleCodeExecute} />
            </Box>
            <Box sx={{ height: '300px', minHeight: '300px' }}>
              <EmbeddedTerminal height="100%" />
            </Box>
          </Box>
          <Box sx={{ p: 2, borderTop: '1px solid #3e3e42' }}>
            <ChatInterface messages={messages} onSend={handleAgentRequest} />
          </Box>
        </Grid>
        
        {/* Right Sidebar - Agent Status */}
        <Grid item xs={3} sx={{ borderLeft: '1px solid #3e3e42', bgcolor: '#252526', overflow: 'auto' }}>
          <Box sx={{ p: 2 }}>
            <AgentStatus status={agentStatus} />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}

export default App;

