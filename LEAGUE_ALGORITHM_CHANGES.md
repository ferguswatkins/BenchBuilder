# League Algorithm Changes Analysis

## Overview
This document outlines how the league rules for "Friends of Joseph E Aoun" (League ID: 281565) affect our draft algorithms and value calculations.

## Key League Settings

### Basic Configuration
- **Teams**: 14 (vs typical 10-12)
- **Scoring**: Full PPR (1 point per reception)
- **Roster**: QB, WR, WR, RB, RB, TE, W/R/T, K, DEF, BN(6), IR(2)

### Critical Scoring Differences
1. **Interceptions**: -1 point (vs typical -2)
2. **Full PPR**: 1 point per reception (increases WR/RB value)
3. **Distance-based kicking**: 50+ yard FGs worth 5 points
4. **Defense points allowed**: Custom scoring tiers

## Algorithm Changes Made

### 1. Scoring Service Updates (`scoring_service.py`)

#### New Features:
- **League-specific scoring rules** for exact point calculations
- **Distance-based field goal scoring** (3/3/3/4/5 points by distance)
- **Updated interception penalty** (-1 vs -2)
- **Full PPR implementation** (1 point per reception)

#### Impact:
- More accurate fantasy point projections
- Better kicker evaluation with distance-based scoring
- Enhanced WR/RB valuations due to full PPR

### 2. VOR Service Updates (`vor_service.py`)

#### New Features:
- **14-team league defaults** (vs 12-team)
- **League-specific roster construction**:
  - QB: 14 starters
  - RB: 42 starters (28 base + 14 flex eligible)
  - WR: 42 starters (28 base + 14 flex eligible)  
  - TE: 28 starters (14 base + 14 flex eligible)
  - K/DEF: 14 starters each
- **Position scarcity multipliers**:
  - RB/WR: 1.2x (high scarcity due to flex + 14 teams)
  - TE: 1.1x (moderate scarcity)
  - QB: 1.0x (standard)
  - K/DEF: 0.8x (streaming positions)
- **Adjusted VOR calculations** accounting for position scarcity

#### Impact:
- More accurate replacement levels for 14-team league
- Better position scarcity modeling
- Enhanced flex position value calculations

### 3. Configuration System (`config/league_rules.py`)

#### New Features:
- **Centralized league configuration**
- **Position scarcity functions**
- **Replacement level calculations**
- **Roster construction definitions**

## How These Changes Affect Draft Strategy

### 1. Running Backs & Wide Receivers
- **Higher Value**: Full PPR + position scarcity (1.2x multiplier)
- **Deeper Replacement Levels**: 42 starters each vs typical 24-36
- **Flex Competition**: W/R/T flex increases demand

### 2. Tight Ends  
- **Moderate Boost**: Flex eligibility + scarcity (1.1x multiplier)
- **28 starters** vs typical 12, but still scarce at top

### 3. Quarterbacks
- **Standard Value**: 1 per team, no major changes
- **Replacement Level**: Rank 24 (14 starters + ~10 backups)

### 4. Kickers & Defenses
- **Streaming Positions**: 0.8x multiplier reflects lower priority
- **Distance-based Kicking**: Accuracy from 50+ yards more valuable

### 5. Bench Depth
- **6 Bench Spots**: More roster flexibility
- **2 IR Spots**: Can stash injured players
- **14 Teams**: Waiver wire thinner, bench depth more important

## Replacement Level Calculations

### Position-Specific Replacement Ranks:
- **QB**: Rank 24 (14 starters + 10 quality backups)
- **RB**: Rank 62 (28 starters + 14 flex + 20 backups)
- **WR**: Rank 67 (28 starters + 14 flex + 25 backups)
- **TE**: Rank 43 (14 starters + 14 flex + 15 backups)
- **K/DEF**: Rank 20 (streaming positions)

## Draft Implications

### Early Rounds (1-3)
- **RB/WR Premium**: Scarcity multipliers make elite players more valuable
- **Positional Flexibility**: W/R/T flex adds strategic complexity
- **14-Team Scarcity**: Top-tier talent disappears faster

### Middle Rounds (4-8)  
- **TE Strategy**: Position scarcity makes quality TEs more valuable
- **Depth Building**: 6 bench spots allow for more speculative picks
- **Bye Week Planning**: 14 teams mean thinner waiver wire

### Late Rounds (9+)
- **Streaming Positions**: K/DEF have lower priority (0.8x multiplier)
- **Handcuffs**: More valuable due to thin waiver wire
- **Upside Plays**: IR spots allow injury stashing

## Testing Recommendations

1. **Projection Accuracy**: Test scoring calculations against actual results
2. **VOR Validation**: Compare rankings to expert consensus
3. **Position Scarcity**: Validate multipliers against draft data
4. **Replacement Levels**: Monitor if calculations match draft patterns

## Files Modified

1. **`config/league_rules.py`** - League configuration and rules
2. **`services/scoring_service.py`** - Updated scoring algorithms  
3. **`services/vor_service.py`** - Enhanced VOR calculations
4. **`config/__init__.py`** - Package initialization

## Next Steps

1. Test algorithms with sample projection data
2. Validate scoring calculations
3. Compare VOR rankings to expert consensus
4. Monitor draft results for accuracy validation
