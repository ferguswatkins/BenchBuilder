import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Grid,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Sports as SportsIcon,
  TrendingUp as TrendingUpIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [sampleDataLoaded, setSampleDataLoaded] = useState(false);

  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      await ApiService.healthCheck();
      setBackendStatus('connected');
      
      // Check if sample data exists
      try {
        const rankings = await ApiService.getVORRankings({ limit: 1 });
        setSampleDataLoaded(rankings.vor_rankings.length > 0);
      } catch {
        setSampleDataLoaded(false);
      }
    } catch (error) {
      setBackendStatus('error');
    }
  };

  const handleLoadSampleData = async () => {
    setIsLoading(true);
    try {
      const result = await ApiService.uploadSampleData();
      if (result.error) {
        console.error('Error loading sample data:', result.error);
      } else {
        setSampleDataLoaded(true);
      }
    } catch (error) {
      console.error('Error loading sample data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const featureCards = [
    {
      title: 'Player Rankings',
      description: 'View VOR-based rankings with fantasy points and position analysis',
      icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/rankings'),
      color: '#1976d2',
    },
    {
      title: 'Draft Preparation',
      description: 'Get draft targets, value tiers, and round-by-round strategy',
      icon: <SportsIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/draft'),
      color: '#2e7d32',
    },
    {
      title: 'Player Comparison',
      description: 'Compare players across different scoring systems and value metrics',
      icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/compare'),
      color: '#ed6c02',
    },
  ];

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Fantasy Draft Co-Pilot
      </Typography>
      <Typography variant="h6" component="h2" gutterBottom align="center" color="text.secondary">
        AI-Powered Fantasy Football Draft Intelligence
      </Typography>

      {/* Backend Status */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
        {backendStatus === 'checking' && (
          <Alert severity="info" sx={{ display: 'flex', alignItems: 'center' }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            Connecting to backend...
          </Alert>
        )}
        {backendStatus === 'connected' && (
          <Alert severity="success">
            Backend connected successfully!
            {sampleDataLoaded && (
              <Chip label="Sample Data Loaded" color="success" size="small" sx={{ ml: 1 }} />
            )}
          </Alert>
        )}
        {backendStatus === 'error' && (
          <Alert severity="error">
            Cannot connect to backend. Make sure your FastAPI server is running on port 8000.
          </Alert>
        )}
      </Box>

      {/* Sample Data Loading */}
      {backendStatus === 'connected' && !sampleDataLoaded && (
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
          <Card sx={{ p: 2, backgroundColor: '#fff3e0' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <UploadIcon sx={{ fontSize: 40, color: '#ed6c02', mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                Load Sample Data
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Load sample projection data to start using the fantasy tools
              </Typography>
              <Button
                variant="contained"
                onClick={handleLoadSampleData}
                disabled={isLoading}
                startIcon={isLoading ? <CircularProgress size={20} /> : <UploadIcon />}
              >
                {isLoading ? 'Loading...' : 'Load Sample Data'}
              </Button>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Feature Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
          gap: 4,
        }}
      >
        {featureCards.map((card, index) => (
          <Card
            key={index}
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              cursor: 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
              },
            }}
            onClick={card.action}
          >
            <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
              <Box sx={{ color: card.color, mb: 2 }}>
                {card.icon}
              </Box>
              <Typography variant="h5" component="h3" gutterBottom>
                {card.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {card.description}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* System Capabilities */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" component="h3" gutterBottom align="center">
          Current System Capabilities
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' },
            gap: 2,
            mt: 2,
          }}
        >
          {[
            'Upload & parse projection CSVs (any format)',
            'Calculate fantasy points (Standard, PPR, Half-PPR, Custom)',
            'Generate VOR-based rankings and draft targets',
            'Compare players across scoring systems',
            'Provide value tiers and position-specific rankings',
            'Support multiple league sizes and roster constructions',
          ].map((capability, index) => (
            <Chip
              key={index}
              label={capability}
              color="primary"
              variant="outlined"
              sx={{ width: '100%', justifyContent: 'flex-start' }}
            />
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default HomePage;
