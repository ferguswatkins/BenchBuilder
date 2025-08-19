# Fantasy Draft Co-Pilot - Technical Implementation Plan

## Overview
This document outlines the incremental development plan for building the Fantasy Draft Co-Pilot application, split into Backend (BE) and Frontend (FE) components with manual verification steps.

## Required Accounts & API Keys

### 1. Yahoo Fantasy Sports API
- **Where to get**: [Yahoo Developer Network](https://developer.yahoo.com/fantasysports/)
- **Steps**:
  1. Create a Yahoo Developer account at developer.yahoo.com
  2. Go to "My Apps" and create a new application
  3. Select "Fantasy Sports" API
  4. Choose "Installed Application" for desktop app or "Web Application" for web app
  5. Get your `Client ID` and `Client Secret`
  6. Set redirect URI (e.g., `http://localhost:3000/auth/callback`)
- **Required Scopes**: `fspt-r` (Fantasy Sports Read)
- **Rate Limits**: 999 requests per hour per IP
- **Documentation**: https://developer.yahoo.com/fantasysports/guide/

### 2. LLM API (Choose One)
#### Option A: OpenAI API
- **Where to get**: [OpenAI Platform](https://platform.openai.com/)
- **Steps**:
  1. Create account at platform.openai.com
  2. Add payment method (required for API access)
  3. Generate API key in "API Keys" section
  4. Recommended model: `gpt-4o-mini` (cost-effective for explanations)
- **Cost**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens

#### Option B: Anthropic Claude API
- **Where to get**: [Anthropic Console](https://console.anthropic.com/)
- **Steps**:
  1. Create account at console.anthropic.com
  2. Add payment method
  3. Generate API key
  4. Recommended model: `claude-3-haiku` (fast and cost-effective)
- **Cost**: ~$0.25 per 1M input tokens, $1.25 per 1M output tokens

### 3. Projection Data Sources (Choose One or More)
#### Option A: FantasyPros API
- **Where to get**: [FantasyPros Developer](https://www.fantasypros.com/api/)
- **Cost**: $20/month for basic access
- **Data**: Expert consensus rankings, projections, ADP

#### Option B: ESPN/Yahoo Public Data
- **Where to get**: Public endpoints (no key required)
- **Note**: May require web scraping, check terms of service
- **Data**: Basic projections and ADP

#### Option C: Manual CSV Import (MVP)
- **Where to get**: Export from FantasyPros, Yahoo, or ESPN
- **Cost**: Free
- **Data**: Static projections for testing

---

## Phase 1: Backend Foundation (Days 1-3)

### Deliverable 1.1: Project Setup & Environment
**Goal**: Working Python environment with basic FastAPI server

**Tasks**:
- [ ] Initialize Python project with virtual environment
- [ ] Install FastAPI, uvicorn, python-dotenv, requests
- [ ] Create basic FastAPI app with health check endpoint
- [ ] Set up environment variables for API keys
- [ ] Create basic project structure

**Manual Verification**:
```bash
# Start server
uvicorn main:app --reload

# Test health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Files Created**:
- `backend/main.py`
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/config.py`

### Deliverable 1.2: Yahoo OAuth Integration
**Goal**: Successfully authenticate with Yahoo API and fetch user leagues

**Tasks**:
- [ ] Implement OAuth 2.0 flow for Yahoo
- [ ] Create endpoints for auth initiation and callback
- [ ] Store and refresh access tokens
- [ ] Test league data retrieval

**Manual Verification**:
```bash
# Start auth flow
curl http://localhost:8000/auth/yahoo
# Should redirect to Yahoo login

# After callback, test league fetch
curl http://localhost:8000/api/leagues
# Expected: List of user's fantasy leagues
```

**Files Created**:
- `backend/auth/yahoo_auth.py`
- `backend/models/league.py`
- `backend/routes/auth.py`

### Deliverable 1.3: Basic Data Models
**Goal**: Define core data structures for players, leagues, and projections

**Tasks**:
- [ ] Create Pydantic models for Player, League, Projection, ADP
- [ ] Implement data validation and serialization
- [ ] Create mock data for testing

**Manual Verification**:
```python
# Test data model creation
from models.player import Player
player = Player(id=1, name="Josh Allen", position="QB", team="BUF")
print(player.json())
```

**Files Created**:
- `backend/models/player.py`
- `backend/models/league.py`
- `backend/models/projection.py`
- `backend/models/draft.py`

---

## Phase 2: Core Backend Logic (Days 4-7)

### Deliverable 2.1: Projection Data Ingestion
**Goal**: Load and normalize projection data from CSV or API

**Tasks**:
- [ ] Create CSV parser for projection data
- [ ] Implement data normalization (different sources → common format)
- [ ] Add data validation and error handling
- [ ] Create endpoint to upload/refresh projections

**Manual Verification**:
```bash
# Upload projections
curl -X POST -F "file=@projections.csv" http://localhost:8000/api/projections/upload
# Expected: {"message": "Uploaded 500 player projections"}

# Fetch projections
curl http://localhost:8000/api/projections?position=QB
# Expected: List of QB projections
```

**Files Created**:
- `backend/services/projection_service.py`
- `backend/routes/projections.py`
- `backend/utils/csv_parser.py`

### Deliverable 2.2: Points Calculator
**Goal**: Convert projections to fantasy points using league scoring rules

**Tasks**:
- [ ] Implement scoring rule engine
- [ ] Calculate fantasy points for each player
- [ ] Handle different league types (PPR, Standard, etc.)
- [ ] Create endpoint to test scoring calculations

**Manual Verification**:
```bash
# Calculate points for a player
curl -X POST http://localhost:8000/api/calculate-points \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "league_id": "abc123"}'
# Expected: {"player_id": 1, "projected_points": 287.5}
```

**Files Created**:
- `backend/services/scoring_service.py`
- `backend/models/scoring_rules.py`

### Deliverable 2.3: VOR (Value Over Replacement) Engine
**Goal**: Calculate VOR and create player tiers

**Tasks**:
- [ ] Implement replacement level calculation
- [ ] Calculate VOR for each player by position
- [ ] Create tiering algorithm
- [ ] Add endpoints for VOR and tier data

**Manual Verification**:
```bash
# Get VOR rankings
curl http://localhost:8000/api/vor-rankings?league_id=abc123
# Expected: Players ranked by VOR with tier assignments

# Get specific position tiers
curl http://localhost:8000/api/tiers?position=RB&league_id=abc123
# Expected: RB players grouped by tiers
```

**Files Created**:
- `backend/services/vor_service.py`
- `backend/services/tier_service.py`

---

## Phase 3: Draft Intelligence (Days 12-15) - MOVED AFTER FRONTEND

### Deliverable 3.1: ADP Integration and Availability Modeling
**Goal**: Predict player availability at future picks

**Tasks**:
- [ ] Integrate ADP data (CSV or API)
- [ ] Implement availability probability calculations
- [ ] Create draft simulation engine
- [ ] Add endpoints for availability predictions

**Manual Verification**:
```bash
# Get availability predictions
curl http://localhost:8000/api/availability?draft_position=8&round=2&league_id=abc123
# Expected: Players with availability percentages

# Run draft simulation
curl -X POST http://localhost:8000/api/simulate-draft \
  -H "Content-Type: application/json" \
  -d '{"draft_position": 8, "league_size": 12, "rounds": 6}'
# Expected: Multiple simulated draft scenarios
```

**Files Created**:
- `backend/services/adp_service.py`
- `backend/services/availability_service.py`
- `backend/services/simulation_service.py`

### Deliverable 3.2: Pick Recommendation Engine
**Goal**: Generate ranked pick recommendations with reasoning

**Tasks**:
- [ ] Implement pick scoring algorithm
- [ ] Calculate roster construction needs
- [ ] Generate top-N recommendations
- [ ] Create structured reasoning data for LLM

**Manual Verification**:
```bash
# Get pick recommendations
curl -X POST http://localhost:8000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "league_id": "abc123",
    "draft_position": 8,
    "current_round": 2,
    "current_roster": ["Josh Allen", "Christian McCaffrey"],
    "available_players": ["Stefon Diggs", "Travis Kelce", "Saquon Barkley"]
  }'
# Expected: Top 5 recommendations with scores and reasoning
```

**Files Created**:
- `backend/services/recommendation_service.py`
- `backend/models/recommendation.py`

### Deliverable 3.3: LLM Integration for Explanations
**Goal**: Generate human-readable explanations for recommendations

**Tasks**:
- [ ] Integrate with chosen LLM API (OpenAI or Anthropic)
- [ ] Create prompt templates for explanations
- [ ] Implement explanation generation
- [ ] Add caching to reduce API costs

**Manual Verification**:
```bash
# Get explanation for a recommendation
curl -X POST http://localhost:8000/api/explain-pick \
  -H "Content-Type: application/json" \
  -d '{
    "player": "Stefon Diggs",
    "reasoning": {
      "vor": 45.2,
      "tier": 1,
      "availability_risk": 0.15,
      "roster_need": "high"
    }
  }'
# Expected: "Take Stefon Diggs: Last WR in Tier 1; 85% chance your RB targets return next round."
```

**Files Created**:
- `backend/services/llm_service.py`
- `backend/templates/explanation_prompts.py`

---

## Phase 4: Real-time Draft Features (Days 16-18) - MOVED AFTER FRONTEND

### Deliverable 4.1: WebSocket Implementation
**Goal**: Real-time updates during draft

**Tasks**:
- [ ] Add WebSocket support to FastAPI
- [ ] Implement draft state management
- [ ] Create real-time recommendation updates
- [ ] Handle multiple concurrent drafts

**Manual Verification**:
```javascript
// Test WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/draft/abc123');
ws.onmessage = (event) => console.log(JSON.parse(event.data));

// Simulate pick update
fetch('/api/draft/abc123/pick', {
  method: 'POST',
  body: JSON.stringify({player_id: 1, team_id: 'team1'}),
  headers: {'Content-Type': 'application/json'}
});
// Expected: WebSocket receives updated recommendations
```

**Files Created**:
- `backend/websocket/draft_ws.py`
- `backend/services/draft_state_service.py`

### Deliverable 4.2: Draft State Management
**Goal**: Track picks and update recommendations in real-time

**Tasks**:
- [ ] Implement draft board state tracking
- [ ] Handle pick validation and updates
- [ ] Recalculate recommendations after each pick
- [ ] Add undo/redo functionality

**Manual Verification**:
```bash
# Add a pick
curl -X POST http://localhost:8000/api/draft/abc123/pick \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "team_id": "team1", "round": 1, "pick": 8}'

# Get updated draft state
curl http://localhost:8000/api/draft/abc123/state
# Expected: Current draft board with all picks

# Undo last pick
curl -X POST http://localhost:8000/api/draft/abc123/undo
# Expected: Previous state restored
```

---

## Phase 5: Frontend Foundation (Days 8-11) - ✅ MOSTLY COMPLETE!

### Deliverable 5.1: React App Setup ✅ COMPLETE
**Goal**: Basic React application with routing

**Tasks**:
- ✅ Create React app with TypeScript
- ✅ Set up routing (React Router)
- ✅ Install UI library (Material-UI)
- ✅ Create basic layout and navigation
- ✅ Set up API client (axios)

**Manual Verification**:
```bash
# Start development server
npm start
# ✅ App loads at http://localhost:3000

# Navigate to different routes
# ✅ /rankings, /draft, /compare pages load with sidebar navigation
```

**Files Created**:
- ✅ `frontend/src/App.tsx` - Main app with routing and Material-UI theme
- ✅ `frontend/src/components/Layout/Layout.tsx` - Responsive sidebar layout
- ✅ `frontend/src/services/api.ts` - Complete API service for backend
- ✅ `frontend/src/types/index.ts` - TypeScript interfaces for all data

### Deliverable 5.2: API Integration and VOR Display ✅ COMPLETE
**Goal**: Connect to backend and display fantasy data

**Tasks**:
- ✅ Set up API client for backend communication
- ✅ Create services for VOR, projections, and scoring APIs
- ✅ Display VOR rankings from working backend
- ✅ Add backend connection status checking

**Manual Verification**:
- ✅ Frontend loads VOR rankings from http://localhost:8000/api/vor/rankings
- ✅ Player data displays correctly (name, position, VOR, fantasy points)
- ✅ Backend connection status shown on home page
- ✅ Sample data loading functionality works

**Files Created**:
- ✅ `frontend/src/services/api.ts` - Complete API service with all endpoints
- ✅ `frontend/src/pages/HomePage.tsx` - Backend connection and status checking
- ✅ Enhanced with backend integration and sample data loading

### Deliverable 5.3: Interactive Player Rankings ✅ COMPLETE
**Goal**: Rich player rankings interface with your VOR data

**Tasks**:
- ✅ Create sortable player rankings table
- ✅ Add position filtering and search
- ✅ Display VOR, fantasy points, and value tiers
- ✅ Add scoring type switching (Standard/PPR/Half-PPR)
- ✅ Implement advanced filtering and visual design

**Manual Verification**:
- ✅ Rankings table shows all players with VOR data from backend
- ✅ Sorting works (VOR, fantasy points, position rank, overall rank)
- ✅ Position filters work (QB, RB, WR, TE, K, DST)
- ✅ Player search finds players by name and team
- ✅ Value tier colors/groupings are visible with color coding
- ✅ Scoring type switching changes rankings in real-time
- ✅ Tier filtering works (Elite, High, Medium, Low, Below Replacement)

**Files Created**:
- ✅ `frontend/src/pages/RankingsPage.tsx` - Complete interactive rankings interface
- ✅ Professional table with sorting, filtering, search, and visual indicators
- ✅ Real-time data integration with backend VOR APIs

### Deliverable 5.4: Draft Preparation Dashboard ⏳ NEXT SESSION
**Goal**: Pre-draft tools using your backend data

**Tasks**:
- [ ] Display draft targets by round/position using `/api/vor/draft-targets`
- [ ] Show value tiers visualization using `/api/vor/value-tiers`
- [ ] Add player comparison tool using `/api/vor/compare-players`
- [ ] Create "my draft plan" interface with user preferences
- [ ] Add draft strategy recommendations based on VOR data

**Manual Verification**:
- [ ] Draft targets load from /api/vor/draft-targets with round/position inputs
- [ ] Value tiers display with Elite/High/Medium/Low groupings and visual indicators
- [ ] Player comparison shows VOR differences and scoring breakdowns
- [ ] Draft plan saves user preferences and shows recommended strategies
- [ ] All features integrate seamlessly with existing backend APIs

**Files to Create**:
- `frontend/src/pages/DraftPage.tsx` - Main draft preparation interface
- `frontend/src/components/Draft/DraftTargets.tsx` - Round-by-round targets
- `frontend/src/components/Draft/ValueTiers.tsx` - Visual tier groupings
- `frontend/src/components/Draft/PlayerComparison.tsx` - Side-by-side comparisons

---

## Phase 6: Live Draft Interface (Days 19-22) - ENHANCED WITH BACKEND DATA

### Deliverable 6.1: Draft Board UI
**Goal**: Visual draft board with pick tracking

**Tasks**:
- [ ] Create draft board grid
- [ ] Display picks in real-time
- [ ] Show current pick indicator
- [ ] Add pick entry (manual hotkeys)

**Manual Verification**:
- [ ] Draft board displays 12x16 grid (12 teams, 16 rounds)
- [ ] Picks appear in correct positions
- [ ] Current pick is highlighted
- [ ] Hotkeys work (D for drafted, U for undo)

**Files Created**:
- `frontend/src/components/Draft/DraftBoard.tsx`
- `frontend/src/components/Draft/PickEntry.tsx`
- `frontend/src/hooks/useHotkeys.ts`

### Deliverable 6.2: Recommendation Panel
**Goal**: Display AI-powered pick recommendations

**Tasks**:
- [ ] Create recommendations display
- [ ] Show player details and reasoning
- [ ] Add LLM explanations
- [ ] Implement what-if queries

**Manual Verification**:
- [ ] Top 5 recommendations displayed with scores
- [ ] Each recommendation shows VOR, tier, ADP delta
- [ ] LLM explanations are clear and helpful
- [ ] What-if queries work ("What if I take QB now?")

**Files Created**:
- `frontend/src/components/Draft/RecommendationPanel.tsx`
- `frontend/src/components/Draft/PlayerCard.tsx`
- `frontend/src/components/Draft/WhatIfQuery.tsx`

### Deliverable 6.3: Real-time Updates
**Goal**: WebSocket integration for live updates

**Tasks**:
- [ ] Implement WebSocket client
- [ ] Handle real-time recommendation updates
- [ ] Update UI when picks are made
- [ ] Show connection status

**Manual Verification**:
- [ ] WebSocket connects successfully
- [ ] Recommendations update when picks are made
- [ ] UI shows "Connected" status
- [ ] Handles reconnection on network issues

**Files Created**:
- `frontend/src/hooks/useWebSocket.ts`
- `frontend/src/services/websocket.ts`

---

## Phase 7: Polish & Deployment (Days 23-25)

### Deliverable 7.1: Error Handling & Testing
**Goal**: Robust error handling and basic tests

**Tasks**:
- [ ] Add comprehensive error handling
- [ ] Create loading states and error messages
- [ ] Write unit tests for core functions
- [ ] Add integration tests

**Manual Verification**:
- [ ] App handles API errors gracefully
- [ ] Loading spinners show during API calls
- [ ] Error messages are user-friendly
- [ ] Tests pass: `npm test` and `pytest`

### Deliverable 7.2: Deployment Setup
**Goal**: Deploy backend and frontend

**Tasks**:
- [ ] Create Docker configuration
- [ ] Set up environment variables
- [ ] Deploy backend (Railway, Render, or similar)
- [ ] Deploy frontend (Vercel, Netlify, or similar)
- [ ] Configure CORS and security

**Manual Verification**:
- [ ] Backend accessible at production URL
- [ ] Frontend connects to production backend
- [ ] OAuth flow works in production
- [ ] All features work end-to-end

**Files Created**:
- `backend/Dockerfile`
- `frontend/.env.production`
- `docker-compose.yml`

---

## Development Environment Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

---

## Testing Strategy

### Manual Testing Checklist
- [ ] OAuth flow completes successfully
- [ ] League data loads correctly
- [ ] Projections import without errors
- [ ] VOR calculations match expected values
- [ ] Recommendations update in real-time
- [ ] WebSocket connection is stable
- [ ] UI is responsive on different screen sizes
- [ ] Error states display helpful messages

### Automated Testing
- **Backend**: pytest for API endpoints and business logic
- **Frontend**: Jest/React Testing Library for components
- **Integration**: Cypress for end-to-end user flows

---

## Success Metrics

### MVP Success Criteria
- [ ] Successfully authenticate with Yahoo API
- [ ] Load league configuration and player data
- [ ] Generate accurate VOR-based rankings
- [ ] Display real-time pick recommendations
- [ ] Complete a mock draft using the interface
- [ ] LLM explanations are helpful and accurate

### Performance Targets
- [ ] API responses < 500ms for recommendations
- [ ] WebSocket updates < 100ms latency
- [ ] Frontend loads < 2 seconds
- [ ] LLM explanations < 2 seconds
- [ ] Handles 12-team draft without issues

This plan provides a structured, incremental approach to building your Fantasy Draft Co-Pilot with clear verification steps at each phase. Each deliverable builds on the previous ones and can be manually tested to ensure functionality before moving forward.
