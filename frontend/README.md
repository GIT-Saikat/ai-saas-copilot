# Frontend - SaaS Support Copilot

React TypeScript frontend for the SaaS Support Copilot with RAG.

## Features

- 🔍 **Search Interface** - Clean search bar with real-time query processing
- 📊 **Analytics Dashboard** - Real-time statistics and metrics
- 💬 **Answer Display** - Formatted answers with confidence scores
- 📚 **Source Chunks** - Expandable list of retrieved documentation chunks
- 👍 **Feedback System** - Thumbs up/down feedback collection
- 🎨 **Modern UI** - Built with shadcn/ui and Tailwind CSS
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop

## Tech Stack

- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Lucide React** for icons
- **Axios** for API communication

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API URL (optional):
Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Project Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui base components
│   ├── SearchBar.tsx    # Search input component
│   ├── AnswerCard.tsx   # Answer display component
│   ├── ChunksList.tsx   # Source chunks display
│   ├── FeedbackButtons.tsx  # Feedback UI
│   └── StatsBar.tsx      # Analytics dashboard
├── services/
│   └── api.ts           # API service layer
├── types/
│   └── index.ts         # TypeScript type definitions
├── lib/
│   └── utils.ts         # Utility functions
└── App.tsx              # Main application component
```

## Components

### SearchBar
- Input field with search button
- Loading state indicator
- Enter key support
- Auto-focus on mount

### AnswerCard
- Displays generated answer
- Shows confidence score with color coding
- Response time indicator
- Blocked query handling

### ChunksList
- Expandable/collapsible chunks
- Similarity score visualization
- Category and metadata display
- Source information

### FeedbackButtons
- Thumbs up/down buttons
- Disabled after submission
- Thank you confirmation
- Error handling

### StatsBar
- Total queries count
- Average confidence
- Blocked queries
- Feedback statistics
- Auto-refresh every 30 seconds

## API Integration

The frontend communicates with the backend API at `http://localhost:8000` by default.

### Endpoints Used:
- `POST /api/query` - Submit queries
- `POST /api/feedback` - Submit feedback
- `GET /api/analytics` - Get analytics data
- `GET /api/health` - Health check

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Environment Variables

- `REACT_APP_API_URL` - Backend API base URL (default: http://localhost:8000)
