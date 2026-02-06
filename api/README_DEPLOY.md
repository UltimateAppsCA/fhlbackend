# Fantasy League Hockey API – Vercel Deployment Guide

## 1. Prerequisites
- Vercel account (https://vercel.com)
- GitHub repo (recommended for Vercel integration)
- Neon PostgreSQL database (already set up)

## 2. Project Structure
- Place all API code in the `api/` directory (already done)
- Ensure `requirements.txt`, `.env`, and `vercel.json` are in `api/`

## 3. Environment Variables
- In Vercel dashboard, set these for your project:
  - `DATABASE_URL` (your Neon connection string)
  - `SECRET_KEY` (same as in your .env)

## 4. Deploy Steps
1. Push your code to GitHub (or connect local folder to Vercel CLI)
2. Import the repo in Vercel dashboard
3. Set environment variables as above
4. Vercel will auto-detect Python and deploy the FastAPI app

## 5. API Endpoints
- All endpoints are available under `/api/` (e.g., `/api/users/register`)

## 6. Notes
- For production, use a strong `SECRET_KEY` and keep it private
- You may need to adjust Vercel settings for Python version if needed

---
For more, see https://vercel.com/docs/deployments/overview and https://vercel.com/docs/concepts/functions/serverless-functions/python
