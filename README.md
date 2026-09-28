# PocketSmart AI

Home, Party and Jewelry planners powered by Gemini.
Split into two deployable parts:

```
frontend/   Static site (HTML/CSS/JS)  -> GitHub Pages
backend/    Flask API + Gemini         -> Render / Railway / PythonAnywhere
```

The Gemini API key lives only on the backend, never in the frontend.

---

## 1. Run locally

**Backend** (terminal 1):
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # add GEMINI_API_KEY and FLASK_SECRET_KEY
python app.py                     # http://127.0.0.1:5000
```

**Frontend** (terminal 2):
```bash
cd frontend
python -m http.server 8000        # open http://localhost:8000
```

`frontend/js/config.js` automatically uses `http://127.0.0.1:5000` when you
open the site from localhost. The default `CORS_ORIGINS` already allows
`localhost:8000`.

Run tests: `cd backend && pytest`

---

## 2. Deploy the backend (Render example)

1. Push this repo to GitHub.
2. On render.com: **New +** -> **Web Service** -> connect the repo.
3. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Add environment variables:
   - `GEMINI_API_KEY` = your key
   - `FLASK_SECRET_KEY` = output of `python -c "import secrets; print(secrets.token_hex(32))"`
   - `FLASK_ENV` = `production`
   - `CORS_ORIGINS` = `https://<your-github-username>.github.io`  (domain only, no repo path)
   - `GEMINI_MODEL` = a current Gemini Flash model name from AI Studio
5. Deploy and copy the URL, e.g. `https://pocketsmart-api.onrender.com`.
   Check `https://<that-url>/health` returns `{"status":"ok"}`.

(`render.yaml` is included if you prefer Render's Blueprint flow.)

## 3. Point the frontend at the backend

Edit `frontend/js/config.js`:

```js
const PRODUCTION_API_URL = "https://pocketsmart-api.onrender.com";
```

Commit and push.

## 4. Deploy the frontend (GitHub Pages)

1. In your repo: **Settings -> Pages -> Build and deployment -> Source: GitHub Actions**.
2. Push to `main` (any change under `frontend/`). The workflow in
   `.github/workflows/deploy-frontend.yml` publishes the `frontend/` folder.
3. Your site will be at `https://<username>.github.io/<repo>/`.

## 5. Push to GitHub

```bash
git init
git add .
git commit -m "PocketSmart AI: Flask backend + static frontend"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo>.git
git push -u origin main
```

## Troubleshooting

- **CORS error in browser console:** `CORS_ORIGINS` on the backend must exactly match
  your Pages origin (`https://<username>.github.io`), with no trailing slash or repo path.
- **Always see the "safe default" text:** the Gemini key is missing/invalid, or
  `GEMINI_MODEL` is retired. Set a current model name from AI Studio.
- **First request very slow:** free backend tiers sleep when idle; the first call wakes them.
- **Never commit `.env`.** It's gitignored; set secrets in the host's dashboard.
