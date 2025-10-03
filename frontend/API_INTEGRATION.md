# API Integration Guide

## Overview
The frontend is now fully integrated with your backend API at `http://localhost:8000`.

## Changing the API URL

To point to a different backend URL, edit the constant in `lib/api.ts`:

```typescript
export const API_BASE_URL = "http://localhost:8000"
```

Change it to your production URL when deploying:
```typescript
export const API_BASE_URL = "https://api.yourdomain.com"
```

Or use environment variables:
```typescript
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
```

## Features Implemented

### 1. Tasks Management
- **List all tasks**: Automatically fetches on app load
- **Create new task**: Click "New Dataroom" button
- **Display risk level**: Shows 🚩 for risky, ✅ for healthy tasks

### 2. Document Upload
- **Multi-file upload**: Drag & drop or click to browse
- **Real-time upload status**: Shows uploading/success/error states
- **Red flags display**: Automatically shows red flags after processing
- **Individual file tracking**: Each file has its own status

### 3. Chat Interface
- **Send messages**: Ask questions about the dataroom
- **Real-time polling**: Updates every 2 seconds during processing
- **Progress tracking**: Shows "Parsing documents", "Searching index", etc.
- **Reasoning display**: Shows AI's reasoning steps
- **Citations**: Links to source documents with page numbers

### 4. Documents List
- **View all documents**: See all uploaded documents
- **Processing status**: Shows "Processed" or "Processing" badge
- **Red flags summary**: Count and details of red flags per document

### 5. Memo/Summary
- **Live memo**: Auto-updated executive summary
- **Key metrics**: Revenue growth, debt/equity ratio, etc.
- **Export functionality**: Download as PDF/Excel
- **Red flag indicators**: Highlights metrics with 🚩

## API Endpoints Used

- `GET /tasks` - List all tasks
- `POST /tasks` - Create new task
- `GET /tasks/{task_id}/documents` - List documents
- `POST /tasks/{task_id}/documents` - Upload document
- `POST /tasks/{task_id}/chat` - Send chat message
- `GET /chat/{chat_id}/status` - Poll chat status (2s interval)
- `GET /tasks/{task_id}/chat/{chat_id}` - Get chat answer
- `GET /tasks/{task_id}/memo` - Get live memo
- `POST /tasks/{task_id}/memo/export` - Export memo

## Error Handling

All API calls include proper error handling:
- Network errors are caught and displayed to users
- Loading states prevent duplicate requests
- User-friendly error messages

## Type Safety

All API responses are typed with TypeScript interfaces in `types/api.ts`:
- `Task`
- `Document`
- `ChatResponse`
- `ChatStatus`
- `ChatAnswer`
- `Memo`

## Testing

1. Start your backend on `http://localhost:8000`
2. Run the frontend: `pnpm dev`
3. Test the flow:
   - Create a new dataroom
   - Upload documents
   - Chat with the agent
   - View documents and red flags
   - Check the memo/summary

## Notes

- Chat polling runs every 2 seconds until status is "done"
- File uploads use FormData (not JSON)
- All other requests use JSON with proper Content-Type headers
