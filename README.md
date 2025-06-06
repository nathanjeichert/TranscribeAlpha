# TranscribeAlpha

A simple transcript generator using Google's Gemini models. The original Streamlit prototype has been replaced with a small FastAPI backend and a SvelteKit front-end that is built to static files.

## Cloning the Repository

You can obtain the source by cloning the Git repository:

```bash
git clone <REPO_URL>.git
```

Replace `<REPO_URL>` with the actual repository URL. The `.git` suffix ensures
Git fetches the repository history properly for reuse.

## Running Locally

1. Install system packages listed in `packages.txt` (ffmpeg and libsndfile1).
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install frontend dependencies and build the SvelteKit app:

```bash
cd frontend
npm install
npm run build
cd ..
```

4. Export your Gemini API key:

```bash
export GEMINI_API_KEY="YOUR_KEY_HERE"
```

5. Start the server:

```bash
uvicorn backend.server:app --reload
```

6. Open [http://localhost:8000](http://localhost:8000) in your browser and interact with the app.

## Notes

The backend relies on the [Google Gen AI Python SDK](https://googleapis.github.io/python-genai/) for Gemini access.
