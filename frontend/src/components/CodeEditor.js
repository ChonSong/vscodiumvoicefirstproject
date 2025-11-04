import React, { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Box, Button, Paper, Typography } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

function CodeEditor({ onExecute }) {
  const [code, setCode] = useState(`# Welcome to ADK IDE
# Type your Python code here

def hello_world():
    print("Hello from ADK IDE!")
    return "Code executed successfully"

hello_world()
`);
  const editorRef = useRef(null);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
  };

  const handleExecute = () => {
    if (onExecute && code.trim()) {
      onExecute(code);
    }
  };

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#1e1e1e' }}>
      <Box sx={{ p: 1, bgcolor: '#252526', display: 'flex', alignItems: 'center', gap: 2, borderBottom: '1px solid #3e3e42' }}>
        <Button
          variant="contained"
          size="small"
          startIcon={<PlayArrowIcon />}
          onClick={handleExecute}
          sx={{ bgcolor: '#0e639c', '&:hover': { bgcolor: '#1177bb' } }}
        >
          Execute
        </Button>
        <Typography variant="caption" sx={{ color: '#cccccc' }}>
          Python 3.11
        </Typography>
      </Box>
      
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <Editor
          height="100%"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value || '')}
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
      </Box>
    </Paper>
  );
}

export default CodeEditor;

