import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Sports as SportsIcon,
} from '@mui/icons-material';
import ApiService from '../services/api';
import { VORRanking, ScoringType, SortState } from '../types';

const RankingsPage: React.FC = () => {
  const [rankings, setRankings] = useState<VORRanking[]>([]);
  const [filteredRankings, setFilteredRankings] = useState<VORRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [positionFilter, setPositionFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [scoringType, setScoringType] = useState<ScoringType>('ppr');
  const [tierFilter, setTierFilter] = useState<string>('ALL');
  
  // Sort state
  const [sortState, setSortState] = useState<SortState>({
    field: 'overall_rank',
    direction: 'asc',
  });

  const positions = ['ALL', 'QB', 'RB', 'WR', 'TE', 'K', 'DST'];
  const tiers = ['ALL', 'Elite', 'High', 'Medium', 'Low', 'Below Replacement'];

  useEffect(() => {
    loadRankings();
  }, [scoringType]);

  useEffect(() => {
    applyFilters();
  }, [rankings, positionFilter, searchQuery, tierFilter, sortState]);

  const loadRankings = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await ApiService.getVORRankings({
        scoring_type: scoringType,
        num_teams: 12,
        include_flex: true,
        limit: 200,
      });
      setRankings(response.vor_rankings);
    } catch (err: any) {
      setError(err.message || 'Failed to load rankings');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...rankings];

    // Position filter
    if (positionFilter !== 'ALL') {
      filtered = filtered.filter(player => player.player.position === positionFilter);
    }

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(player =>
        player.player.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        player.player.team.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Tier filter
    if (tierFilter !== 'ALL') {
      filtered = filtered.filter(player => player.value_tier === tierFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue: any = a[sortState.field];
      let bValue: any = b[sortState.field];

      // Handle nested player properties
      if (sortState.field === 'fantasy_points' || sortState.field === 'vor' || sortState.field === 'overall_rank') {
        aValue = a[sortState.field];
        bValue = b[sortState.field];
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sortState.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    setFilteredRankings(filtered);
  };

  const handleSort = (field: keyof VORRanking | 'fantasy_points' | 'vor' | 'overall_rank') => {
    setSortState(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'Elite': return '#4caf50'; // Green
      case 'High': return '#2196f3';  // Blue
      case 'Medium': return '#ff9800'; // Orange
      case 'Low': return '#f44336';    // Red
      case 'Below Replacement': return '#757575'; // Grey
      default: return '#757575';
    }
  };

  const formatPoints = (points: number) => points.toFixed(1);
  const formatVOR = (vor: number) => vor > 0 ? `+${vor.toFixed(1)}` : vor.toFixed(1);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Player Rankings
        </Typography>
        <Tooltip title="Refresh Rankings">
          <IconButton onClick={loadRankings} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Filters Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filters & Settings
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
            <FormControl size="small">
              <InputLabel>Scoring Type</InputLabel>
              <Select
                value={scoringType}
                label="Scoring Type"
                onChange={(e) => setScoringType(e.target.value as ScoringType)}
              >
                <MenuItem value="standard">Standard</MenuItem>
                <MenuItem value="ppr">PPR</MenuItem>
                <MenuItem value="half_ppr">Half PPR</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small">
              <InputLabel>Position</InputLabel>
              <Select
                value={positionFilter}
                label="Position"
                onChange={(e) => setPositionFilter(e.target.value)}
              >
                {positions.map(pos => (
                  <MenuItem key={pos} value={pos}>{pos}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small">
              <InputLabel>Value Tier</InputLabel>
              <Select
                value={tierFilter}
                label="Value Tier"
                onChange={(e) => setTierFilter(e.target.value)}
              >
                {tiers.map(tier => (
                  <MenuItem key={tier} value={tier}>{tier}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              size="small"
              label="Search Players"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Name or team..."
            />
          </Box>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Rankings Table */}
      {!loading && !error && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                VOR Rankings ({filteredRankings.length} players)
              </Typography>
              <Chip 
                label={`${scoringType.toUpperCase()} Scoring`} 
                color="primary" 
                icon={<SportsIcon />}
              />
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={sortState.field === 'overall_rank'}
                        direction={sortState.field === 'overall_rank' ? sortState.direction : 'asc'}
                        onClick={() => handleSort('overall_rank')}
                      >
                        Rank
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Player</TableCell>
                    <TableCell>Pos</TableCell>
                    <TableCell>Team</TableCell>
                    <TableCell align="right">
                      <TableSortLabel
                        active={sortState.field === 'fantasy_points'}
                        direction={sortState.field === 'fantasy_points' ? sortState.direction : 'desc'}
                        onClick={() => handleSort('fantasy_points')}
                      >
                        Fantasy Pts
                      </TableSortLabel>
                    </TableCell>
                    <TableCell align="right">
                      <TableSortLabel
                        active={sortState.field === 'vor'}
                        direction={sortState.field === 'vor' ? sortState.direction : 'desc'}
                        onClick={() => handleSort('vor')}
                      >
                        VOR
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Value Tier</TableCell>
                    <TableCell align="center">Pos Rank</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredRankings.map((player) => (
                    <TableRow key={player.player.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {player.overall_rank}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {player.player.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={player.player.position} 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {player.player.team}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {formatPoints(player.fantasy_points)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          variant="body2" 
                          fontWeight="bold"
                          color={player.vor > 0 ? 'success.main' : 'error.main'}
                        >
                          {formatVOR(player.vor)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={player.value_tier}
                          size="small"
                          sx={{
                            backgroundColor: getTierColor(player.value_tier),
                            color: 'white',
                            fontWeight: 'bold',
                          }}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2" color="text.secondary">
                          {player.position_rank}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default RankingsPage;
