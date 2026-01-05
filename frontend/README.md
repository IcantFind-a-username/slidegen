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
├── package.json        # Project config and dependencies
├── vite.config.js      # Vite build config
├── README.md           # This document
└── src/
    ├── main.jsx        # React entry
    ├── App.jsx         # Main app component
    ├── App.css         # Global styles
    └── api/
        └── pptApi.js   # API helper functions
```

## Features

- ✅ Text prompt input
- ✅ Async job creation
- ✅ Status polling display
- ✅ Progress bar
- ✅ Error handling
- ✅ PPTX file download
- ✅ Render report display (collapsible)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Create generation job |
| `/jobs/{job_id}` | GET | Get job status |
| `/jobs/{job_id}/download` | GET | Download PPTX file |
| `/jobs/{job_id}/report` | GET | Get render report |

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

## Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

