import axios, { AxiosResponse } from 'axios';
import {
  VORResponse,
  ValueTierResponse,
  DraftTarget,
  ComparisonResponse,
  ScoringComparison,
  ScoringType,
  ApiResponse
} from '../types';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API service class
export class ApiService {
  // VOR Rankings endpoints
  static async getVORRankings(params: {
    num_teams?: number;
    include_flex?: boolean;
    scoring_type?: ScoringType;
    limit?: number;
  } = {}): Promise<VORResponse> {
    const response = await apiClient.get('/api/vor/rankings', { params });
    return response.data;
  }

  static async getPositionVORRankings(
    position: string,
    params: {
      num_teams?: number;
      scoring_type?: ScoringType;
      limit?: number;
    } = {}
  ): Promise<{ position: string; rankings: any[]; total: number }> {
    const response = await apiClient.get(`/api/vor/position/${position}`, { params });
    return response.data;
  }

  static async getValueTiers(params: {
    scoring_type?: ScoringType;
    num_teams?: number;
  } = {}): Promise<ValueTierResponse> {
    const response = await apiClient.get('/api/vor/value-tiers', { params });
    return response.data;
  }

  static async getDraftTargets(
    round_number: number,
    draft_position: number,
    params: {
      num_teams?: number;
      scoring_type?: ScoringType;
    } = {}
  ): Promise<DraftTarget> {
    const response = await apiClient.get('/api/vor/draft-targets', {
      params: {
        round_number,
        draft_position,
        ...params,
      },
    });
    return response.data;
  }

  static async comparePlayers(
    player_ids: number[],
    scoring_type: ScoringType = 'ppr'
  ): Promise<ComparisonResponse> {
    const response = await apiClient.post('/api/vor/compare-players', {
      player_ids,
      scoring_type,
    });
    return response.data;
  }

  // Scoring endpoints
  static async compareScoringSystem(player_id: number): Promise<ScoringComparison> {
    const response = await apiClient.get(`/api/scoring/compare-systems/${player_id}`);
    return response.data;
  }

  static async calculateAllPoints(params: {
    scoring_type?: ScoringType;
    position?: string;
    limit?: number;
  } = {}): Promise<any> {
    const response = await apiClient.get('/api/scoring/calculate-all', { params });
    return response.data;
  }

  // Projection endpoints
  static async getProjections(params: {
    position?: string;
    team?: string;
    limit?: number;
  } = {}): Promise<any> {
    const response = await apiClient.get('/api/projections/', { params });
    return response.data;
  }

  static async searchPlayers(query: string, limit: number = 20): Promise<any> {
    const response = await apiClient.get('/api/projections/search', {
      params: { q: query, limit },
    });
    return response.data;
  }

  static async uploadSampleData(): Promise<ApiResponse<any>> {
    try {
      const response = await apiClient.post('/api/projections/upload-sample');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  // Yahoo Fantasy API endpoints
  static async importYahooProjections(accessToken: string, leagueKey?: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiClient.post('/api/yahoo/import-projections', 
        leagueKey ? { league_key: leagueKey } : {},
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  }

  static async getYahooGameInfo(accessToken: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiClient.get('/api/yahoo/game-info', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  }

  static async getUserLeagues(accessToken: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiClient.get('/api/leagues', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  }

  // Health check
  static async healthCheck(): Promise<{ status: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  }
}

export default ApiService;
