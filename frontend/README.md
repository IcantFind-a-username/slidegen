# SlideGen Frontend

AI-powered presentation generator frontend interface.

## Requirements

- Node.js 18+ 
- npm or yarn

## Quick Start

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start development server

```bash
npm run dev
```

Frontend will run at: http://localhost:8080

### 3. Make sure backend is running

Backend API should be running at: http://localhost:8000

## Project Structure

```
frontend/
├── index.html          # HTML entry
├── package.json        # Dependencies
├── vite.config.js      # Vite config
└── src/
    ├── main.jsx        # React entry
    ├── App.jsx         # Main component
    ├── App.css         # Styles
    └── api/
        └── pptApi.js   # API client
```

## Features

- ✅ Text prompt input
- ✅ Async job creation
- ✅ Real-time status polling
- ✅ Smooth progress bar animation
- ✅ Error handling
- ✅ PPTX file download

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Create generation job |
| `/jobs/{job_id}` | GET | Get job status & progress |
| `/jobs/{job_id}/download` | GET | Download PPTX file |

## Job Status

- `queued` - In queue
- `generating` / `generating_json` - Generating content
- `rendering` - Rendering PPT
- `done` - Complete
- `failed` - Failed

## Tech Stack

- React 18
- Vite 5
- Native CSS (no UI framework)
- Fetch API
