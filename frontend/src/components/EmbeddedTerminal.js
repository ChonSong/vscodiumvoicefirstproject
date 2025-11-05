import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ClearIcon from '@mui/icons-material/Clear';
import WebSocketConnection from '../services/websocket';

function EmbeddedTerminal({ height = '300px' }) {
  const [output, setOutput] = useState([]);
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [ws, setWs] = useState(null);
  const outputEndRef = useRef(null);
  const commandInputRef = useRef(null);

  useEffect(() => {
    const websocket = new WebSocketConnection({
      onConnect: () => {
        console.log('Terminal: WebSocket connected');
        addOutputLine('Terminal connected. Type commands to execute.', 'info');
      },
      onMessage: (message) => {
        if (message.type === 'terminal_result') {
          if (message.status === 'success') {
            const result = message.data;
            if (result.stdout) {
              addOutputLine(result.stdout, 'output');
            }
            if (result.stderr) {
              addOutputLine(result.stderr, 'error');
            }
            if (result.output) {
              addOutputLine(result.output, 'output');
            }
            if (result.error) {
              addOutputLine(result.error, 'error');
            }
            if (!result.stdout && !result.stderr && !result.output && !result.error) {
              addOutputLine(JSON.stringify(result, null, 2), 'output');
            }
          } else {
            addOutputLine(
              message.message || 'Command execution failed',
              'error'
            );
          }
          setLoading(false);
        } else if (message.type === 'terminal_progress') {
          addOutputLine(message.message, 'info');
        }
      },
      onError: (err) => {
        console.error('Terminal WebSocket error:', err);
        addOutputLine('Connection error', 'error');
        setLoading(false);
      },
    });
    setWs(websocket);

    // Initial welcome message
    addOutputLine('ADK IDE Terminal - BuiltInCodeExecutor Ready', 'info');
    addOutputLine('Type commands to execute in the sandboxed environment.', 'info');

    return () => {
      websocket.disconnect();
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when output changes
    if (outputEndRef.current) {
      outputEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [output]);

  const addOutputLine = (text, type = 'output') => {
    const timestamp = new Date().toLocaleTimeString();
    setOutput((prev) => [
      ...prev,
      { text, type, timestamp },
    ]);
  };

  const handleExecute = () => {
    if (!command.trim() || loading) return;

    // Add command to output
    addOutputLine(`$ ${command}`, 'command');

    // Add to history
    setCommandHistory((prev) => [...prev, command]);
    setHistoryIndex(-1);

    // Execute via WebSocket
    if (ws && ws.ws?.readyState === WebSocket.OPEN) {
      setLoading(true);
      ws.send({
        type: 'terminal_execute',
        request_id: `terminal_${Date.now()}`,
        payload: {
          command: command,
        },
      });
    } else {
      addOutputLine('Terminal not connected. Please wait...', 'error');
    }

    setCommand('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleExecute();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex =
          historyIndex === -1
            ? commandHistory.length - 1
            : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIndex);
        setCommand(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex >= 0) {
        const newIndex = historyIndex + 1;
        if (newIndex >= commandHistory.length) {
          setHistoryIndex(-1);
          setCommand('');
        } else {
          setHistoryIndex(newIndex);
          setCommand(commandHistory[newIndex]);
        }
      }
    }
  };

  const handleClear = () => {
    setOutput([]);
  };

  const getOutputColor = (type) => {
    switch (type) {
      case 'error':
        return '#f48771';
      case 'info':
        return '#4ec9b0';
      case 'command':
        return '#dcdcaa';
      default:
        return '#cccccc';
    }
  };

  return (
    <Paper
      sx={{
        height,
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#1e1e1e',
        borderTop: '1px solid #3e3e42',
      }}
    >
      <Box
        sx={{
          p: 1,
          bgcolor: '#252526',
          borderBottom: '1px solid #3e3e42',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Typography
          variant="subtitle2"
          sx={{ color: '#cccccc', fontWeight: 'bold' }}
        >
          TERMINAL
        </Typography>
        <IconButton
          size="small"
          onClick={handleClear}
          sx={{ color: '#cccccc' }}
          title="Clear terminal"
        >
          <ClearIcon fontSize="small" />
        </IconButton>
      </Box>

      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 1,
          fontFamily: 'monospace',
          fontSize: '12px',
          bgcolor: '#0d1117',
        }}
      >
        {output.map((line, index) => (
          <Box
            key={index}
            sx={{
              color: getOutputColor(line.type),
              mb: 0.5,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {line.type === 'command' ? (
              <Box>
                <Box component="span" sx={{ color: '#4ec9b0' }}>
                  {line.timestamp}
                </Box>{' '}
                <Box component="span" sx={{ color: '#dcdcaa' }}>
                  {line.text}
                </Box>
              </Box>
            ) : (
              <Box>
                {line.type !== 'info' && (
                  <Box component="span" sx={{ color: '#858585', mr: 1 }}>
                    {line.timestamp}
                  </Box>
                )}
                {line.text}
              </Box>
            )}
          </Box>
        ))}
        {loading && (
          <Box sx={{ color: '#4ec9b0' }}>Executing...</Box>
        )}
        <div ref={outputEndRef} />
      </Box>

      <Box
        sx={{
          p: 1,
          bgcolor: '#252526',
          borderTop: '1px solid #3e3e42',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Box
          component="span"
          sx={{
            color: '#4ec9b0',
            fontFamily: 'monospace',
            fontSize: '12px',
            minWidth: '60px',
          }}
        >
          {'>'}
        </Box>
        <TextField
          fullWidth
          inputRef={commandInputRef}
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command..."
          disabled={loading}
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#1e1e1e',
              color: '#cccccc',
              fontFamily: 'monospace',
              fontSize: '12px',
              '& fieldset': {
                borderColor: '#3e3e42',
              },
              '&:hover fieldset': {
                borderColor: '#4ec9b0',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#4ec9b0',
              },
              '&.Mui-disabled': {
                bgcolor: '#2d2d30',
              },
            },
            '& .MuiInputBase-input': {
              color: '#cccccc',
            },
          }}
        />
        <IconButton
          onClick={handleExecute}
          disabled={loading || !command.trim()}
          sx={{
            color: '#4ec9b0',
            '&:hover': { bgcolor: 'rgba(78, 201, 176, 0.1)' },
            '&.Mui-disabled': { color: '#858585' },
          }}
        >
          <PlayArrowIcon fontSize="small" />
        </IconButton>
      </Box>
    </Paper>
  );
}

export default EmbeddedTerminal;

