# Packet Capture Backend

FastAPI backend for the Packet Capture CTF platform.

## Local Setup

Create a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment values from the root `.env.example` into a root `.env`, then set:

```env
DATABASE_URL=postgresql+psycopg://packet_capture:change_this_local_password@localhost:5432/packet_capture_ctf
```

Run migrations:

```bash
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Open:

```txt
http://localhost:8000/docs
```

## Docker

From the project root:

```bash
docker-compose up --build
```

The backend uses the Compose database host `postgres` through `DOCKER_DATABASE_URL`.
