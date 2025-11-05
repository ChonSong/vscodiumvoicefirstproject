import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Collapse,
  TextField,
  InputAdornment,
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import WebSocketConnection from '../services/websocket';

function FileExplorer({ onFileSelect, currentPath = '.' }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [subdirectoryContents, setSubdirectoryContents] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [ws, setWs] = useState(null);
  const pendingRequests = useRef({});
  const currentPathRef = useRef(currentPath);

  // Keep currentPath ref in sync
  useEffect(() => {
    currentPathRef.current = currentPath;
  }, [currentPath]);

  const loadDirectory = React.useCallback((dirPath) => {
    if (!ws || ws.ws?.readyState !== WebSocket.OPEN) {
      return;
    }

    setLoading(true);
    setError(null);
    const requestId = `explorer_${Date.now()}_${Math.random()}`;
    pendingRequests.current[requestId] = dirPath;
    
    ws.send({
      type: 'file_explorer',
      request_id: requestId,
      payload: {
        action: 'list',
        path: dirPath,
      },
    });
  }, [ws]);

  useEffect(() => {
    const websocket = new WebSocketConnection({
      onConnect: () => {
        console.log('FileExplorer: WebSocket connected');
        loadDirectory(currentPathRef.current);
      },
      onMessage: (message) => {
        if (message.type === 'file_explorer_result') {
          const requestId = message.request_id;
          const path = pendingRequests.current[requestId];
          
          if (path) {
            delete pendingRequests.current[requestId];
            
            if (message.status === 'success') {
              const items = message.data.items || [];
              if (path === currentPathRef.current) {
                setFiles(items);
                setError(null);
              } else {
                // Update subdirectory contents
                setSubdirectoryContents(prev => ({
                  ...prev,
                  [path]: items,
                }));
              }
            } else {
              setError(message.message || 'Failed to load directory');
            }
          }
          setLoading(false);
        }
      },
      onError: (err) => {
        console.error('FileExplorer WebSocket error:', err);
        setError('Connection error');
        setLoading(false);
      },
    });
    setWs(websocket);

    return () => {
      websocket.disconnect();
    };
  }, [loadDirectory]);

  useEffect(() => {
    if (ws && ws.ws?.readyState === WebSocket.OPEN) {
      loadDirectory(currentPath);
    }
  }, [currentPath, ws, loadDirectory]);

  const handleRefresh = () => {
    loadDirectory(currentPath);
    // Clear subdirectory cache
    setSubdirectoryContents({});
  };

  const handleFolderClick = (folderPath) => {
    const isExpanded = expandedFolders[folderPath];
    const newExpanded = !isExpanded;
    
    setExpandedFolders({
      ...expandedFolders,
      [folderPath]: newExpanded,
    });

    // Load subdirectory contents when expanding
    if (newExpanded && !subdirectoryContents[folderPath]) {
      loadDirectory(folderPath);
    }
  };

  const handleFileClick = (filePath) => {
    if (onFileSelect) {
      onFileSelect(filePath);
    }
  };

  const filteredFiles = files.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderFileItem = (item, path, depth = 0) => {
    const fullPath = path === '.' ? item.name : `${path}/${item.name}`;
    const isFolder = item.type === 'directory';
    const isExpanded = expandedFolders[fullPath];
    const subItems = subdirectoryContents[fullPath] || [];

    if (isFolder) {
      return (
        <Box key={fullPath}>
          <ListItem
            button
            onClick={() => handleFolderClick(fullPath)}
            sx={{
              py: 0.5,
              pl: depth * 2 + 1,
              '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>
              {isExpanded ? (
                <FolderOpenIcon sx={{ color: '#4ec9b0', fontSize: 20 }} />
              ) : (
                <FolderIcon sx={{ color: '#4ec9b0', fontSize: 20 }} />
              )}
            </ListItemIcon>
            <ListItemText
              primary={item.name}
              primaryTypographyProps={{
                style: { color: '#cccccc', fontSize: '13px' },
              }}
            />
          </ListItem>
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <Box>
              {subItems.length === 0 ? (
                <Box sx={{ pl: depth * 2 + 5, py: 1 }}>
                  <Typography variant="caption" sx={{ color: '#858585' }}>
                    Loading...
                  </Typography>
                </Box>
              ) : (
                subItems.map((subItem) => renderFileItem(subItem, fullPath, depth + 1))
              )}
            </Box>
          </Collapse>
        </Box>
      );
    }

    return (
      <ListItem
        key={fullPath}
        button
        onClick={() => handleFileClick(fullPath)}
        sx={{
          py: 0.5,
          pl: depth * 2 + 1,
          '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
        }}
      >
        <ListItemIcon sx={{ minWidth: 36 }}>
          <InsertDriveFileIcon sx={{ color: '#858585', fontSize: 20 }} />
        </ListItemIcon>
        <ListItemText
          primary={item.name}
          primaryTypographyProps={{
            style: { color: '#cccccc', fontSize: '13px' },
          }}
        />
      </ListItem>
    );
  };

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#1e1e1e',
      }}
    >
      <Box
        sx={{
          p: 1,
          bgcolor: '#252526',
          borderBottom: '1px solid #3e3e42',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Typography
          variant="subtitle2"
          sx={{ color: '#cccccc', fontWeight: 'bold', flex: 1 }}
        >
          EXPLORER
        </Typography>
        <IconButton
          size="small"
          onClick={handleRefresh}
          sx={{ color: '#cccccc' }}
        >
          <RefreshIcon fontSize="small" />
        </IconButton>
      </Box>

      <Box sx={{ p: 1, borderBottom: '1px solid #3e3e42' }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#858585', fontSize: 18 }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#2d2d30',
              color: '#cccccc',
              '& fieldset': {
                borderColor: '#3e3e42',
              },
              '&:hover fieldset': {
                borderColor: '#4ec9b0',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#4ec9b0',
              },
            },
            '& .MuiInputBase-input': {
              color: '#cccccc',
              fontSize: '12px',
            },
          }}
        />
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {loading && files.length === 0 && (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="caption" sx={{ color: '#858585' }}>
              Loading...
            </Typography>
          </Box>
        )}

        {error && (
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#f48771' }}>
              {error}
            </Typography>
          </Box>
        )}

        {!loading && !error && (
          <List dense sx={{ py: 0 }}>
            {filteredFiles.length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="No files found"
                  primaryTypographyProps={{
                    style: { color: '#858585', fontSize: '12px' },
                  }}
                />
              </ListItem>
            ) : (
              filteredFiles.map((item) => renderFileItem(item, currentPath))
            )}
          </List>
        )}
      </Box>
    </Paper>
  );
}

export default FileExplorer;
