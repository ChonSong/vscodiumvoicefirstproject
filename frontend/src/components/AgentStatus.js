import React from 'react';
import { Box, Typography, Paper, Chip, List, ListItem, ListItemText } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';

const agents = [
  { name: 'Human Interaction Agent', status: 'active' },
  { name: 'Developing Agent', status: 'active' },
  { name: 'Code Execution Agent', status: 'active' },
  { name: 'Code Writer Agent', status: 'idle' },
  { name: 'Code Reviewer Agent', status: 'idle' },
  { name: 'Debug Agent', status: 'idle' },
  { name: 'Error Detection Agent', status: 'idle' },
];

function AgentStatus({ status }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon sx={{ color: '#4ec9b0', fontSize: 16 }} />;
      case 'error':
        return <ErrorIcon sx={{ color: '#f48771', fontSize: 16 }} />;
      default:
        return <PendingIcon sx={{ color: '#858585', fontSize: 16 }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h6" sx={{ color: '#cccccc', mb: 2 }}>
        Agent Status
      </Typography>
      
      <Paper sx={{ bgcolor: '#1e1e1e', p: 2 }}>
        <List dense>
          {agents.map((agent) => (
            <ListItem key={agent.name} sx={{ py: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                {getStatusIcon(agent.status)}
                <ListItemText
                  primary={agent.name}
                  primaryTypographyProps={{ sx: { color: '#cccccc', fontSize: '0.875rem' } }}
                />
                <Chip
                  label={agent.status}
                  size="small"
                  color={getStatusColor(agent.status)}
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              </Box>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" sx={{ color: '#cccccc', mb: 2 }}>
          Workflow Status
        </Typography>
        <Paper sx={{ bgcolor: '#1e1e1e', p: 2 }}>
          <Typography variant="body2" sx={{ color: '#858585' }}>
            No active workflows
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}

export default AgentStatus;

