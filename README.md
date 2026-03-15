# Receipt Scanning Application

A mobile-first web app that lets you photograph paper receipts with your phone camera, automatically extracts all values using OCR + AI, and stores them in a searchable expense log — with one-tap export to Workday/HR portals and optional Google Sheets sync.

---

## Features

- **Scan receipts** — take a photo with your phone camera
- **Auto-extraction** — PaddleOCR + Claude AI reads vendor, date, line items, tax, and total
- **Review & edit** — correct any mistakes before saving
- **Expense categories** — tag each receipt (Meals, Travel, Office, Other)
- **History** — search and browse all saved receipts
- **Export to HR** — download Workday-compatible CSV for expense report submission
- **Google Sheets sync** — automatically append each receipt to a Google Sheet
- **Installable PWA** — add to your phone's home screen (no app store needed)
- **Simple UI** — large buttons and text, designed for ease of use

---

## How It Works

```
Phone camera → PaddleOCR (free, local) → Claude AI (structures text into JSON)
                                       ↓ (if low confidence)
                               Claude Vision API (fallback)
```

---

## Setup

### Requirements
- Python 3.11+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

flask db upgrade              # creates the SQLite database
python run.py                 # starts on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # starts on http://localhost:5173
```

Open http://localhost:5173 on your phone or desktop browser.

---

## Google Sheets Integration (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → Create a project
2. Enable the **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → download the JSON credentials file
4. Open your Google Sheet → Share it with the service account email (Editor access)
5. Add to your `backend/.env`:
   ```
   GOOGLE_SHEETS_CREDENTIALS_FILE=/path/to/credentials.json
   GOOGLE_SHEET_ID=your-sheet-id-from-the-url
   ```

Each saved receipt will automatically appear as a new row in the sheet.

---

## Exporting to Workday

From the "My Receipts" screen, tap **Export to HR System** → choose **Workday / HR Portal (CSV)**.

The CSV columns map directly to Workday expense import fields:
- `Transaction Date`, `Supplier`, `Expense Type`, `Amount`, `Currency`, `Tax Amount`, `Memo`, `External Reference ID`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `DATABASE_URL` | No | Defaults to `sqlite:///receipts.db` |
| `UPLOAD_FOLDER` | No | Defaults to `./uploads` |
| `OCR_CONFIDENCE_THRESHOLD` | No | Defaults to `0.70` (below this → Claude Vision fallback) |
| `FLASK_ENV` | No | `development` or `production` |
| `SECRET_KEY` | No | Flask secret key (change in production) |
| `GOOGLE_SHEETS_CREDENTIALS_FILE` | No | Path to service account JSON |
| `GOOGLE_SHEET_ID` | No | Google Sheet ID from the URL |

---

## Running Tests

```bash
cd backend
pip install pytest
pytest tests/
```
