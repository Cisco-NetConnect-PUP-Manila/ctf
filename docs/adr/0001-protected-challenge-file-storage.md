# Protected Challenge File Storage

Status: accepted

Challenge artifacts are private evidence files, so they must never live in the frontend `public/` folder or be exposed before a team unlocks the challenge. We will store only file metadata and an internally generated storage key in PostgreSQL, keep local dev files in backend-controlled storage, and route all participant downloads through the backend access check so the same API can later point to private cloud object storage.
