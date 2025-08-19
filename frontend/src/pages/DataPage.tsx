import React, { useState } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  TextField,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  SportsTennis as YahooIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { ApiService } from '../services/api';

const DataPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [yahooToken, setYahooToken] = useState('');
  const [importStats, setImportStats] = useState<{
    players_fetched?: number;
    projections_stored?: number;
  } | null>(null);

  const handleUploadSampleData = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      const result = await ApiService.uploadSampleData();
      
      if (result.error) {
        setMessage({ type: 'error', text: result.error });
      } else {
        setMessage({ 
          type: 'success', 
          text: 'Sample data uploaded successfully! 12 players loaded with realistic projections.' 
        });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to upload sample data' });
    } finally {
      setLoading(false);
    }
  };

  const handleImportYahooData = async () => {
    if (!yahooToken.trim()) {
      setMessage({ type: 'error', text: 'Please enter your Yahoo access token' });
      return;
    }

    setLoading(true);
    setMessage(null);
    setImportStats(null);
    
    try {
      const result = await ApiService.importYahooProjections(yahooToken.trim());
      
      if (result.error) {
        setMessage({ type: 'error', text: result.error });
      } else {
        const data = result.data;
        setImportStats({
          players_fetched: data?.data?.players_fetched,
          projections_stored: data?.data?.projections_stored,
        });
        setMessage({ 
          type: 'success', 
          text: data?.message || 'Yahoo data imported successfully!' 
        });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to import Yahoo data' });
    } finally {
      setLoading(false);
    }
  };

  const handleClearData = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      // Use the projections clear endpoint
      const response = await fetch('http://localhost:8000/api/projections/clear', {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'All projection data cleared successfully' });
        setImportStats(null);
      } else {
        setMessage({ type: 'error', text: 'Failed to clear data' });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to clear data' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <UploadIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Data Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Import player projection data from various sources
        </Typography>
      </Box>

      {/* Status Message */}
      {message && (
        <Alert 
          severity={message.type} 
          sx={{ mb: 3 }}
          onClose={() => setMessage(null)}
        >
          {message.text}
        </Alert>
      )}

      {/* Import Stats */}
      {importStats && (
        <Card sx={{ mb: 3, bgcolor: 'success.light', color: 'success.contrastText' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <CheckIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Import Statistics
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="Players Fetched" 
                  secondary={importStats.players_fetched || 'N/A'} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Projections Stored" 
                  secondary={importStats.projections_stored || 'N/A'} 
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      )}

      {/* Data Sources */}
      <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' } }}>
        
        {/* Sample Data */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <RefreshIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Sample Data
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Load test data with 12 realistic player projections for development and testing.
            </Typography>
            
            <List dense sx={{ mb: 2 }}>
              <ListItem>
                <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                <ListItemText primary="12 players across all positions" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                <ListItemText primary="Realistic 2024 projections" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                <ListItemText primary="Instant availability" />
              </ListItem>
            </List>
            
            <Button
              variant="contained"
              color="primary"
              onClick={handleUploadSampleData}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
              fullWidth
            >
              {loading ? 'Loading...' : 'Load Sample Data'}
            </Button>
          </CardContent>
        </Card>

        {/* Yahoo Fantasy API */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <YahooIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Yahoo Fantasy API
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Import real player data from Yahoo Fantasy Sports API using your access token.
            </Typography>
            
            <TextField
              fullWidth
              label="Yahoo Access Token"
              value={yahooToken}
              onChange={(e) => setYahooToken(e.target.value)}
              placeholder="Enter your Yahoo OAuth access token"
              sx={{ mb: 2 }}
              type="password"
            />
            
            <List dense sx={{ mb: 2 }}>
              <ListItem>
                <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                <ListItemText primary="Real NFL player data" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                <ListItemText primary="Current season information" />
              </ListItem>
              <ListItem>
                <ListItemIcon><ErrorIcon color="warning" /></ListItemIcon>
                <ListItemText primary="Requires Yahoo OAuth token" />
              </ListItem>
            </List>
            
            <Button
              variant="contained"
              color="secondary"
              onClick={handleImportYahooData}
              disabled={loading || !yahooToken.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <YahooIcon />}
              fullWidth
            >
              {loading ? 'Importing...' : 'Import Yahoo Data'}
            </Button>
          </CardContent>
        </Card>
      </Box>

      {/* Data Management */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Management
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Manage your current projection data
          </Typography>
          
          <Divider sx={{ my: 2 }} />
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              color="error"
              onClick={handleClearData}
              disabled={loading}
              startIcon={<ErrorIcon />}
            >
              Clear All Data
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            How to Get Yahoo Access Token
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="1. Complete Yahoo OAuth Flow"
                secondary="Visit /auth/yahoo to authenticate with Yahoo Fantasy"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="2. Extract Access Token"
                secondary="From the OAuth callback, copy the access_token value"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="3. Import Data"
                secondary="Paste the token above and click 'Import Yahoo Data'"
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DataPage;
