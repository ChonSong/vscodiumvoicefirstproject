import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, List, ListItem } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

function ChatInterface({ messages, onSend }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (input.trim() && onSend) {
      onSend({ message: input });
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getMessageColor = (type) => {
    switch (type) {
      case 'success':
        return '#4ec9b0';
      case 'error':
        return '#f48771';
      case 'info':
        return '#569cd6';
      default:
        return '#cccccc';
    }
  };

  return (
    <Paper sx={{ height: '300px', display: 'flex', flexDirection: 'column', bgcolor: '#1e1e1e' }}>
      <Box sx={{ p: 1, bgcolor: '#252526', borderBottom: '1px solid #3e3e42' }}>
        <Typography variant="caption" sx={{ color: '#cccccc' }}>
          Agent Chat
        </Typography>
      </Box>
      
      <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        <List dense>
          {messages.length === 0 && (
            <ListItem>
              <Typography variant="body2" sx={{ color: '#858585', fontStyle: 'italic' }}>
                No messages yet. Start a conversation with the agent...
              </Typography>
            </ListItem>
          )}
          {messages.map((msg, idx) => (
            <ListItem key={idx} sx={{ py: 0.5 }}>
              <Typography
                variant="body2"
                sx={{
                  color: getMessageColor(msg.type),
                  fontFamily: msg.type === 'success' ? 'monospace' : 'inherit',
                  fontSize: msg.type === 'success' ? '0.75rem' : '0.875rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {msg.text}
              </Typography>
            </ListItem>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Box>
      
      <Box sx={{ p: 1, bgcolor: '#252526', borderTop: '1px solid #3e3e42', display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Type your message to the agent..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#1e1e1e',
              color: '#cccccc',
              '& fieldset': { borderColor: '#3e3e42' },
            },
          }}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          startIcon={<SendIcon />}
          sx={{ bgcolor: '#0e639c', '&:hover': { bgcolor: '#1177bb' } }}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
}

export default ChatInterface;

