# TRA Train Delay/Cancellation Monitor

A web service that monitors Taiwan Railway (TRA) trains for delays and cancellations on a regular interval, and notifies users via LINE Messaging API.

Users manage their watch rules (by train number or time period) through a web frontend, and receive push notifications on LINE when a watched train is delayed or cancelled.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, APScheduler
- **Frontend**: React, TypeScript, Vite, React Query
- **Database**: SQLite
- **Notifications**: LINE Messaging API (push messages)
- **Data Source**: TDX (Transport Data eXchange) — Taiwan MOTC open data platform

## Project Structure

```
tra/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings from .env
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── models.py                # DB models (users, watch_rules, alert_history, cache)
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── auth.py              # Register, login, JWT, LINE user ID linking
│   │   │   ├── watch_rules.py       # CRUD for watch rules
│   │   │   ├── trains.py            # Station list, search, train types
│   │   │   ├── alerts.py            # Alert history
│   │   │   └── line_webhook.py      # LINE follow/unfollow webhook
│   │   ├── services/
│   │   │   ├── tdx.py               # TDX API client (OAuth + endpoints)
│   │   │   ├── checker.py           # Core logic: match rules vs live delay data
│   │   │   ├── scheduler.py         # APScheduler (polls every 3 min)
│   │   │   ├── notifier.py          # LINE Messaging API push messages
│   │   │   └── reference_cache.py   # Cache stations + train types from TDX
│   │   └── utils/
│   │       └── security.py          # Password hashing, JWT helpers
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── api/
        │   ├── client.ts            # Axios with JWT interceptor
        │   ├── types.ts             # TypeScript interfaces
        │   └── hooks.ts             # React Query hooks
        └── pages/
            ├── Login.tsx
            ├── Register.tsx
            ├── Dashboard.tsx         # Current status of watched trains
            ├── WatchRules.tsx        # List, toggle, delete rules
            ├── AddRule.tsx           # Create a new watch rule
            ├── EditRule.tsx          # Edit an existing rule
            └── Settings.tsx          # Link LINE account
```

## Prerequisites

Before running the project, you need accounts/credentials from two external services:

### 1. TDX (Transport Data eXchange)

1. Register at https://tdx.transportdata.tw
2. Get your **Client ID** and **Client Secret** from the member dashboard

### 2. LINE Messaging API

1. Create a LINE Official Account at https://developers.line.biz
2. Enable the Messaging API for the account
3. Get the **Channel Access Token** (long-lived) and **Channel Secret**
4. Set the webhook URL to `https://your-domain/api/line/webhook`

## Setup

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env and fill in your credentials:
#   TDX_CLIENT_ID, TDX_CLIENT_SECRET
#   SECRET_KEY (any random string for JWT signing)
#   LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`. Swagger UI is available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend.

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register with email + password |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/auth/line-user-id` | Link LINE account by user ID |

### Watch Rules
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/rules` | List all rules |
| POST | `/api/rules` | Create a rule |
| GET | `/api/rules/{id}` | Get a rule |
| PUT | `/api/rules/{id}` | Update a rule |
| DELETE | `/api/rules/{id}` | Delete a rule |
| PATCH | `/api/rules/{id}/toggle` | Enable/disable a rule |

### Alerts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/alerts` | Recent alerts for current user |
| GET | `/api/alerts/rule/{id}` | Alerts for a specific rule |

### Trains (reference data)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/trains/stations` | All TRA stations |
| GET | `/api/trains/stations/search?q=` | Search stations by name |
| GET | `/api/trains/types` | Train type codes |

### LINE Webhook
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/line/webhook` | LINE follow/unfollow events |

## Watch Rule Types

- **By train number**: Monitor a specific train (e.g., train 126) on selected days of the week
- **By time period**: Monitor all trains at a given station within a time window (e.g., Taipei station, 07:00–09:00, weekdays)

## How Notifications Work

1. The scheduler runs `check_all_rules()` every 3 minutes
2. It fetches live delay and alert data from TDX
3. For each active watch rule, it checks if any matching train is delayed or cancelled
4. If a match is found, it records an alert and sends a LINE push message to the user (if their LINE account is linked)
5. Duplicate alerts within a 10-minute window are suppressed

## Linking LINE

Users link their LINE account in the Settings page:

1. Add the LINE Official Account as a friend
2. The bot's webhook logs the user's LINE User ID
3. The user pastes their LINE User ID in Settings to complete the link
4. When a user unfollows the bot, their LINE account is automatically unlinked
