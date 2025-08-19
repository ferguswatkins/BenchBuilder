# VOR System Test Commands

## 1. Get Overall VOR Rankings (Top 10)
```bash
curl "http://localhost:8000/api/vor/rankings?limit=10"
```

## 2. Get VOR Rankings for RBs Only
```bash
curl "http://localhost:8000/api/vor/position/RB?limit=5"
```

## 3. Get VOR Rankings for QBs
```bash
curl "http://localhost:8000/api/vor/position/QB"
```

## 4. Compare Specific Players (CMC vs Josh Allen vs Cooper Kupp)
```bash
curl -X POST "http://localhost:8000/api/vor/compare-players" \
  -H "Content-Type: application/json" \
  -d '{
    "player_ids": [4, 1, 7],
    "scoring_type": "ppr"
  }'
```

## 5. Get Draft Targets for Round 1, Pick 8
```bash
curl "http://localhost:8000/api/vor/draft-targets?round_number=1&draft_position=8"
```

## 6. Get Draft Targets for Round 3, Pick 5
```bash
curl "http://localhost:8000/api/vor/draft-targets?round_number=3&draft_position=5"
```

## 7. Get Value Tiers (All Players Grouped by Value)
```bash
curl "http://localhost:8000/api/vor/value-tiers"
```

## 8. Get VOR Rankings for 10-team League
```bash
curl "http://localhost:8000/api/vor/rankings?num_teams=10&limit=10"
```

## Expected Results:

### VOR Rankings Should Show:
- **Elite Tier (VOR >= 100)**: Christian McCaffrey, Cooper Kupp, Josh Allen
- **High Tier (VOR >= 50)**: Other top players like Lamar Jackson, Tyreek Hill
- **Medium/Low Tiers**: Remaining players

### Key VOR Concepts Demonstrated:
1. **Position Scarcity**: QBs might have lower VOR despite high fantasy points (12 teams need 12 QBs)
2. **Replacement Level**: RBs/WRs typically have higher VOR due to more roster spots needed
3. **Draft Strategy**: Players with highest VOR are best values regardless of total points

### Sample Expected VOR Values:
- **Christian McCaffrey (RB)**: ~150+ VOR (Elite)
- **Cooper Kupp (WR)**: ~140+ VOR (Elite) 
- **Josh Allen (QB)**: ~80+ VOR (High) - Lower due to QB scarcity being less impactful
- **Travis Kelce (TE)**: ~120+ VOR (Elite) - TE premium position

### Draft Targets:
- **Round 1, Pick 8**: Should suggest elite RB/WR options
- **Round 3, Pick 5**: Should suggest high-value players still available

The VOR system will show which players provide the most value relative to what you could get as a replacement, which is crucial for optimal draft strategy!
