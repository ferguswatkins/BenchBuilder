# Test Commands for Projection and Scoring Systems

## 1. Upload Sample Projections
```bash
curl -X POST "http://localhost:8000/api/projections/upload-sample" \
  -H "Content-Type: application/json"
```

## 2. Get All Projections
```bash
curl "http://localhost:8000/api/projections/"
```

## 3. Get QB Projections Only
```bash
curl "http://localhost:8000/api/projections/?position=QB&limit=10"
```

## 4. Search for a Player
```bash
curl "http://localhost:8000/api/projections/search?q=Josh%20Allen"
```

## 5. Get Projection Statistics
```bash
curl "http://localhost:8000/api/projections/stats"
```

## 6. Calculate Points for All Players (PPR)
```bash
curl "http://localhost:8000/api/scoring/calculate-all?scoring_type=ppr"
```

## 7. Calculate Points for QBs Only (Standard)
```bash
curl "http://localhost:8000/api/scoring/calculate-all?scoring_type=standard&position=QB"
```

## 8. Compare Scoring Systems for a Player (ID 1 = Josh Allen)
```bash
curl "http://localhost:8000/api/scoring/compare-systems/1"
```

## 9. Get Detailed Scoring Breakdown for a Player
```bash
curl "http://localhost:8000/api/scoring/breakdown/1?scoring_type=ppr"
```

## 10. Get Default Scoring Rules
```bash
curl "http://localhost:8000/api/scoring/default-rules"
```

## 11. Create Custom League
```bash
curl -X POST "http://localhost:8000/api/scoring/create-custom-league" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom League",
    "scoring_type": "ppr",
    "custom_rules": {
      "pass_td": 6.0,
      "rush_td": 6.0,
      "rec_td": 6.0,
      "reception": 0.5
    }
  }'
```

## 12. Test Sample CSV Format
```bash
curl "http://localhost:8000/api/projections/sample-csv"
```

## Expected Results:
- Command 1: Should upload 12 sample players with projections
- Command 2: Should return all players with projection data
- Command 3: Should return only QB projections (Josh Allen, Lamar Jackson, Jalen Hurts)
- Command 4: Should find Josh Allen specifically
- Command 6: Should return all players ranked by fantasy points in PPR format
- Command 8: Should show Josh Allen scores higher in PPR than Standard (due to rushing)
- Command 9: Should show detailed breakdown of Josh Allen's 287.5 projected points

## Key Players in Sample Data:
1. Josh Allen (QB) - 287.5 FPTS
2. Lamar Jackson (QB) - 276.8 FPTS  
3. Jalen Hurts (QB) - 274.3 FPTS
4. Christian McCaffrey (RB) - 287.0 FPTS
5. Cooper Kupp (WR) - 294.7 FPTS
