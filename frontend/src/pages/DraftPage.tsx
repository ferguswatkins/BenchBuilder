import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Grid2 as Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Compare as CompareIcon,
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import { ApiService } from '../services/api';
import {
  DraftTarget,
  ValueTierResponse,
  ComparisonResponse,
  ScoringType,
} from '../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`draft-tabpanel-${index}`}
      aria-labelledby={`draft-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DraftPage: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [scoringType, setScoringType] = useState<ScoringType>('ppr');
  const [numTeams, setNumTeams] = useState(12);
  const [draftPosition, setDraftPosition] = useState(1);
  const [selectedRound, setSelectedRound] = useState(1);
  
  // Data state
  const [draftTargets, setDraftTargets] = useState<DraftTarget | null>(null);
  const [valueTiers, setValueTiers] = useState<ValueTierResponse | null>(null);
  const [comparisonPlayers, setComparisonPlayers] = useState<number[]>([]);
  const [comparisonResult, setComparisonResult] = useState<ComparisonResponse | null>(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compareDialogOpen, setCompareDialogOpen] = useState(false);

  // Load initial data
  useEffect(() => {
    loadDraftData();
  }, [scoringType, numTeams]);

  useEffect(() => {
    if (selectedRound && draftPosition) {
      loadDraftTargets();
    }
  }, [selectedRound, draftPosition, scoringType, numTeams]);

  const loadDraftData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [tiersData] = await Promise.all([
        ApiService.getValueTiers({ scoring_type: scoringType, num_teams: numTeams }),
      ]);
      setValueTiers(tiersData);
    } catch (err: any) {
      setError(err.message || 'Failed to load draft data');
    } finally {
      setLoading(false);
    }
  };

  const loadDraftTargets = async () => {
    try {
      const targets = await ApiService.getDraftTargets(selectedRound, draftPosition, {
        num_teams: numTeams,
        scoring_type: scoringType,
      });
      setDraftTargets(targets);
    } catch (err: any) {
      console.error('Failed to load draft targets:', err);
    }
  };

  const handleComparePlayer = (playerId: number) => {
    if (comparisonPlayers.includes(playerId)) {
      setComparisonPlayers(comparisonPlayers.filter(id => id !== playerId));
    } else if (comparisonPlayers.length < 5) {
      setComparisonPlayers([...comparisonPlayers, playerId]);
    }
  };

  const runComparison = async () => {
    if (comparisonPlayers.length < 2) return;
    
    try {
      const result = await ApiService.comparePlayers(comparisonPlayers, scoringType);
      setComparisonResult(result);
      setCompareDialogOpen(true);
    } catch (err: any) {
      setError(err.message || 'Failed to compare players');
    }
  };

  const clearComparison = () => {
    setComparisonPlayers([]);
    setComparisonResult(null);
  };

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      'Elite': '#4caf50',
      'High': '#2196f3',
      'Medium': '#ff9800',
      'Low': '#f44336',
      'Below Replacement': '#9e9e9e',
    };
    return colors[tier] || '#757575';
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (loading && !valueTiers) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <TrophyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Draft Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Prepare for your draft with value tiers, targets, and player comparisons
        </Typography>
      </Box>

      {/* Configuration Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Scoring Type</InputLabel>
                <Select
                  value={scoringType}
                  onChange={(e) => setScoringType(e.target.value as ScoringType)}
                >
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="ppr">PPR</MenuItem>
                  <MenuItem value="half_ppr">Half PPR</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid xs={12} sm={3}>
              <TextField
                fullWidth
                label="League Size"
                type="number"
                value={numTeams}
                onChange={(e) => setNumTeams(parseInt(e.target.value))}
                inputProps={{ min: 8, max: 16 }}
              />
            </Grid>
            <Grid xs={12} sm={3}>
              <TextField
                fullWidth
                label="Draft Position"
                type="number"
                value={draftPosition}
                onChange={(e) => setDraftPosition(parseInt(e.target.value))}
                inputProps={{ min: 1, max: numTeams }}
              />
            </Grid>
            <Grid xs={12} sm={3}>
              <TextField
                fullWidth
                label="Round"
                type="number"
                value={selectedRound}
                onChange={(e) => setSelectedRound(parseInt(e.target.value))}
                inputProps={{ min: 1, max: 20 }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Player Comparison Bar */}
      {comparisonPlayers.length > 0 && (
        <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <CompareIcon />
                <Typography variant="h6">
                  Players Selected for Comparison ({comparisonPlayers.length}/5)
                </Typography>
                <Box sx={{ ml: 2 }}>
                  {comparisonPlayers.map((id, index) => (
                    <Chip
                      key={id}
                      label={`Player ${id}`}
                      onDelete={() => handleComparePlayer(id)}
                      sx={{ mr: 1, bgcolor: 'white', color: 'primary.main' }}
                    />
                  ))}
                </Box>
              </Box>
              <Box>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={runComparison}
                  disabled={comparisonPlayers.length < 2}
                  sx={{ mr: 1 }}
                >
                  Compare
                </Button>
                <Button variant="outlined" color="inherit" onClick={clearComparison}>
                  Clear
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Draft Targets" />
          <Tab label="Value Tiers" />
          <Tab label="Draft Strategy" />
        </Tabs>
      </Box>

      {/* Draft Targets Tab */}
      <TabPanel value={activeTab} index={0}>
        {draftTargets && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Round {selectedRound}, Pick {draftTargets.overall_pick}
            </Typography>
            
            {/* Top Targets */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Top Draft Targets
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Rank</TableCell>
                        <TableCell>Player</TableCell>
                        <TableCell>Position</TableCell>
                        <TableCell>Fantasy Points</TableCell>
                        <TableCell>VOR</TableCell>
                        <TableCell>Tier</TableCell>
                        <TableCell>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {draftTargets.top_targets.slice(0, 10).map((player) => (
                        <TableRow key={player.player.id}>
                          <TableCell>{player.overall_rank}</TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2" fontWeight="bold">
                                {player.player.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {player.player.team}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{player.player.position}</TableCell>
                          <TableCell>{player.fantasy_points.toFixed(1)}</TableCell>
                          <TableCell>{player.vor.toFixed(1)}</TableCell>
                          <TableCell>
                            <Chip
                              label={player.value_tier}
                              size="small"
                              sx={{ bgcolor: getTierColor(player.value_tier), color: 'white' }}
                            />
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              onClick={() => handleComparePlayer(player.player.id)}
                              variant={comparisonPlayers.includes(player.player.id) ? 'contained' : 'outlined'}
                            >
                              {comparisonPlayers.includes(player.player.id) ? 'Selected' : 'Compare'}
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Targets by Position */}
            <Typography variant="h6" gutterBottom>
              Targets by Position
            </Typography>
            {Object.entries(draftTargets.targets_by_position).map(([position, players]) => (
              <Accordion key={position}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">
                    {position} ({players.length} players)
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Rank</TableCell>
                          <TableCell>Player</TableCell>
                          <TableCell>Fantasy Points</TableCell>
                          <TableCell>VOR</TableCell>
                          <TableCell>Tier</TableCell>
                          <TableCell>Action</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {players.slice(0, 5).map((player) => (
                          <TableRow key={player.player.id}>
                            <TableCell>{player.overall_rank}</TableCell>
                            <TableCell>{player.player.name}</TableCell>
                            <TableCell>{player.fantasy_points.toFixed(1)}</TableCell>
                            <TableCell>{player.vor.toFixed(1)}</TableCell>
                            <TableCell>
                              <Chip
                                label={player.value_tier}
                                size="small"
                                sx={{ bgcolor: getTierColor(player.value_tier), color: 'white' }}
                              />
                            </TableCell>
                            <TableCell>
                              <Button
                                size="small"
                                onClick={() => handleComparePlayer(player.player.id)}
                                variant={comparisonPlayers.includes(player.player.id) ? 'contained' : 'outlined'}
                              >
                                {comparisonPlayers.includes(player.player.id) ? 'Selected' : 'Compare'}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </TabPanel>

      {/* Value Tiers Tab */}
      <TabPanel value={activeTab} index={1}>
        {valueTiers && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Value Tiers
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Players grouped by their draft value relative to replacement level
            </Typography>

            {Object.entries(valueTiers.value_tiers).map(([tierName, players]) => (
              <Accordion key={tierName} defaultExpanded={tierName === 'Elite'}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Chip
                      label={tierName}
                      sx={{ bgcolor: getTierColor(tierName), color: 'white', fontWeight: 'bold' }}
                    />
                    <Typography variant="h6">
                      {players.length} players
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Rank</TableCell>
                          <TableCell>Player</TableCell>
                          <TableCell>Position</TableCell>
                          <TableCell>Fantasy Points</TableCell>
                          <TableCell>VOR</TableCell>
                          <TableCell>Action</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {players.map((player) => (
                          <TableRow key={player.player.id}>
                            <TableCell>{player.overall_rank}</TableCell>
                            <TableCell>
                              <Box>
                                <Typography variant="body2" fontWeight="bold">
                                  {player.player.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {player.player.team}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>{player.player.position}</TableCell>
                            <TableCell>{player.fantasy_points.toFixed(1)}</TableCell>
                            <TableCell>{player.vor.toFixed(1)}</TableCell>
                            <TableCell>
                              <Button
                                size="small"
                                onClick={() => handleComparePlayer(player.player.id)}
                                variant={comparisonPlayers.includes(player.player.id) ? 'contained' : 'outlined'}
                              >
                                {comparisonPlayers.includes(player.player.id) ? 'Selected' : 'Compare'}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </TabPanel>

      {/* Draft Strategy Tab */}
      <TabPanel value={activeTab} index={2}>
        <Typography variant="h5" gutterBottom>
          Draft Strategy Guide
        </Typography>
        
        <Grid container spacing={3}>
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Your Draft Setup
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="League Size"
                      secondary={`${numTeams} teams`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Scoring System"
                      secondary={scoringType.toUpperCase()}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Draft Position"
                      secondary={`Pick ${draftPosition} of ${numTeams}`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Current Focus"
                      secondary={`Round ${selectedRound} preparation`}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Draft Tips
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Value Over Replacement"
                      secondary="Focus on VOR rather than just projected points"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Tier-Based Drafting"
                      secondary="Draft the last player in a tier before moving to next position"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Position Scarcity"
                      secondary="Consider how quickly positions are being drafted"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Flexible Strategy"
                      secondary="Adapt your plan based on how the draft unfolds"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Player Comparison Dialog */}
      <Dialog
        open={compareDialogOpen}
        onClose={() => setCompareDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Player Comparison</DialogTitle>
        <DialogContent>
          {comparisonResult && (
            <Box>
              {comparisonResult.best_value && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Best Value: {comparisonResult.best_value.player.name} (VOR: {comparisonResult.best_value.vor.toFixed(1)})
                </Alert>
              )}
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Player</TableCell>
                      <TableCell>Position</TableCell>
                      <TableCell>Fantasy Points</TableCell>
                      <TableCell>VOR</TableCell>
                      <TableCell>Tier</TableCell>
                      <TableCell>Overall Rank</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {comparisonResult.comparison.map((player) => (
                      <TableRow key={player.player.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {player.player.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {player.player.team}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{player.player.position}</TableCell>
                        <TableCell>{player.fantasy_points.toFixed(1)}</TableCell>
                        <TableCell>{player.vor.toFixed(1)}</TableCell>
                        <TableCell>
                          <Chip
                            label={player.value_tier}
                            size="small"
                            sx={{ bgcolor: getTierColor(player.value_tier), color: 'white' }}
                          />
                        </TableCell>
                        <TableCell>{player.overall_rank}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompareDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DraftPage;
