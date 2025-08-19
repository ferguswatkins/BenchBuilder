// Core player and fantasy types
export interface Player {
  id: number;
  name: string;
  position: string;
  team: string;
}

export interface PlayerProjection {
  passing_yards?: number;
  passing_tds?: number;
  interceptions?: number;
  rushing_yards?: number;
  rushing_tds?: number;
  receptions?: number;
  receiving_yards?: number;
  receiving_tds?: number;
  field_goals?: number;
  extra_points?: number;
  def_touchdowns?: number;
  def_interceptions?: number;
  def_fumbles?: number;
  def_sacks?: number;
  def_safeties?: number;
  points_allowed?: number;
}

export interface VORRanking {
  overall_rank: number;
  player: Player;
  fantasy_points: number;
  vor: number;
  value_tier: string;
  position_rank: number;
  replacement_level: number;
}

export interface VORResponse {
  vor_rankings: VORRanking[];
  metadata: {
    total_players: number;
    league_size: number;
    replacement_levels: Record<string, number>;
    roster_construction: Record<string, number>;
  };
}

export interface ValueTier {
  [tierName: string]: {
    player: Player;
    fantasy_points: number;
    vor: number;
    overall_rank: number;
  }[];
}

export interface ValueTierResponse {
  value_tiers: ValueTier;
  tier_counts: Record<string, number>;
}

export interface DraftTarget {
  round: number;
  pick: number;
  overall_pick: number;
  targets_by_position: Record<string, VORRanking[]>;
  top_targets: VORRanking[];
}

export interface PlayerComparison {
  player: Player;
  fantasy_points: number;
  vor: number;
  value_tier: string;
  overall_rank: number;
}

export interface ComparisonResponse {
  comparison: PlayerComparison[];
  best_value: {
    player: Player;
    vor: number;
  } | null;
  vor_differences: any[];
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// Scoring types
export type ScoringType = 'standard' | 'ppr' | 'half_ppr';

export interface ScoringComparison {
  player: Player;
  scoring_breakdown: Record<ScoringType, {
    total_points: number;
    breakdown: Record<string, number>;
  }>;
}

// League configuration
export interface League {
  id: string;
  name: string;
  num_teams: number;
  scoring_type: ScoringType;
  scoring_rules?: Record<string, number>;
}

// UI State types
export interface FilterState {
  position: string;
  searchQuery: string;
  minVOR: number;
  maxVOR: number;
  tier: string;
}

export interface SortState {
  field: keyof VORRanking | 'fantasy_points' | 'vor' | 'overall_rank';
  direction: 'asc' | 'desc';
}
