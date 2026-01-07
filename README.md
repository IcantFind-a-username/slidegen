# SlideGen - AI-Powered Presentation Generator

Transform text prompts into professional PowerPoint presentations using GPT-4 and DALL-E 3.

## Features

- **AI Content Generation**: GPT-4o-mini generates structured slide content
- **AI Image Generation**: DALL-E 3 creates custom illustrations for slides
- **Professional Design**: Modern layouts with intelligent typography
- **Real-time Progress**: Smooth progress tracking during generation
- **Multiple Slide Types**: Title, content, two-column, section dividers, and closing slides

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API Key

### Setup

1. **Backend Setup**

```bash
cd backend
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

2. **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

3. **Open Browser**

Navigate to `http://localhost:8080`

## Usage

1. Enter a prompt (e.g., "Create a presentation about artificial intelligence")
2. Wait for AI generation (30-60 seconds)
3. Download your professional PowerPoint file

## Architecture

- **Backend**: FastAPI + OpenAI GPT-4o-mini + DALL-E 3
- **Frontend**: React + Vite
- **Rendering**: python-pptx with custom design system

## Tech Stack

- Python 3.9+
- FastAPI
- OpenAI API (GPT-4o-mini, DALL-E 3)
- python-pptx
- React
- Vite

