# PROVA-GT

**AI-Assisted Grounded Theory: A Provenance-Centered Approach for Traceability, Transparency and Auditability**

PROVA-GT is a provenance-centered visual analytics system for AI-assisted grounded theory (GT). It supports the full GT workflow:

- **Forward process** - LLM-assisted open coding, hierarchical categorization, and linkage analysis for theory building.
- **Backward process** - an agentic provenance workflow (ProvAgent) that lets researchers trace, verify, and refine coding results in a unified interface.

The UI (branded *PatternWeave*) contains four coordinated views - Content View, Hierarchy View, Linkage View, and the ProvAgent memo/chat panel.

This repository contains the web prototype: a Nuxt 3 frontend and five lightweight Flask backend services.

## Architecture

| Service | Port | File | LLM / API |
| --- | --- | --- | --- |
| File upload & coding service | 8000 | `backend/file.py` | Moonshot |
| Embedding & UMAP service | 5003 | `backend/app_api.py` | DashScope |
| Batch embedding service | 5004 | `backend/overview_api.py` | DashScope |
| Memo & linkage service | 5002 | `backend/app_memo.py` | Moonshot |
| Agentic chatbot (ProvAgent) | 5005 | `backend/app_ai_chat.py` | DeepSeek |

## Prerequisites

- Python 3.10+ (tested with 3.12)
- Node.js 18+ (tested with 20)
- API keys for the providers you want to use (see [API keys](#api-keys))

## Backend setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# Configure your API keys
cp .env.example .env        # then edit .env and fill in your keys
```

## Start the backend services

Run each service in its own terminal, from the `backend` directory:

```bash
python file.py           # port 8000
python app_api.py        # port 5003
python overview_api.py   # port 5004
python app_memo.py       # port 5002
python app_ai_chat.py    # port 5005
```

## Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

## Try it with the demo data

No API key? No problem - you can still explore the views with the pre-computed coding results:

1. In the UI, click **Upload CSV** (top toolbar) and select one of the files in `frontend/public/`:
   - `code_library.csv` - first-order codes with life stages.
   - `social.csv` - a larger coded corpus (entrepreneurial inspiration interviews).
   - `coding-data.csv` - hierarchical second-order codes, ideal for the Linkage View.
2. Explore the Hierarchy View (tag clouds, cards, stacked bars) and the Linkage View (Sankey diagram).

To run the full LLM-assisted pipeline:

1. Make sure `MOONSHOT_API_KEY` is set in `backend/.env`.
2. Upload your own `.txt` interview transcripts with the header upload button, or use the sample transcripts in `frontend/uploads/` (`alanna_chapman.txt`, `bailey_peryman.txt`).
3. Configure the prompt in the Content View and run open coding. The results are exported as a CSV and loaded into the views automatically.

## API keys

Copy `backend/.env.example` to `backend/.env` and fill in the keys for the services you use:

| Variable | Used by | Where to obtain |
| --- | --- | --- |
| `MOONSHOT_API_KEY` | `file.py`, `app_memo.py` | https://platform.moonshot.cn |
| `DASHSCOPE_API_KEY` | `app_api.py`, `overview_api.py` | https://bailian.console.aliyun.com |
| `DEEPSEEK_API_KEY` | `app_ai_chat.py` | https://platform.deepseek.com |
| `SILICONFLOW_API_KEY` | `file_sf.py` (optional variant) | https://cloud.siliconflow.cn |

The `.env` file is git-ignored; never commit real keys.

## Optional: local-model backend variants

The `backend` directory also contains legacy variants that load embedding models locally (e.g. `app_md.py`, `app_La.py`, `app_nv.py`, `app_ro.py`, `overview_*.py`) and alternate coding services (`file_ds.py` for DeepSeek, `file_sf.py` for SiliconFlow, `file_cache.py` for cached prompts). They are not required for the standard workflow above. If you want to run the local-model variants, install the extra dependencies:

```bash
pip install -r requirements-variants.txt
```

## Notes

- Run the backend scripts from the `backend` directory: they resolve the upload and public folders relative to their location.
- The UI hardcodes `localhost` service ports; all five services must run on the same machine as the browser by default.
- If a service cannot find a required API key it prints an error at startup and exits.

## Citation

If you use this system in your research, please cite the accompanying paper: *AI-Assisted Grounded Theory: A Provenance-Centered Approach for Traceability, Transparency and Auditability* (2026).

