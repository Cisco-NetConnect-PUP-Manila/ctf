#!/usr/bin/env bash
# ==============================================================================
# Build All CTF Platform & Challenge Images on Worker (Linux VM)
# New monorepo structure:
#   - Frontend (Next.js): repo root  → local/ctf-frontend:latest
#   - Backend (FastAPI):  ./backend/ → local/ctf-backend:latest
#   - Challenges:         ~/ctf-challenges/ctf-web-challs/ciscoconnect/
# ==============================================================================
set -euo pipefail

DOMAIN="${1:-packetcapture.xyz}"
API_BASE_URL="https://api.${DOMAIN}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHALLENGES_ROOT="${HOME}/ctf-challenges/ctf-web-challs/ciscoconnect"

echo "======================================================================"
echo ">>> Building CTF Platform Images"
echo "    Domain:          ${DOMAIN}"
echo "    API Base URL:    ${API_BASE_URL}"
echo "    Repo Root:       ${REPO_ROOT}"
echo "======================================================================"

echo ""
echo ">>> 1. Building Frontend (Next.js from repo root)..."
docker build \
  --build-arg NEXT_PUBLIC_API_BASE_URL="${API_BASE_URL}" \
  -t local/ctf-frontend:latest \
  "${REPO_ROOT}"

echo ""
echo ">>> 2. Building Backend (FastAPI from ./backend/)..."
docker build \
  -t local/ctf-backend:latest \
  "${REPO_ROOT}/backend"

echo ""
echo ">>> 3. Building Challenge Images from ${CHALLENGES_ROOT}..."

docker build -t local/ctf-abandoned-project:latest "${CHALLENGES_ROOT}/abandoned_project"
docker build -t local/ctf-black-box:latest         "${CHALLENGES_ROOT}/black_box"
docker build -t local/ctf-corrupt-corporate:latest "${CHALLENGES_ROOT}/corrupt_corporate"
docker build -t local/ctf-forgotten-router:latest  "${CHALLENGES_ROOT}/forgotten_router"
docker build -t local/ctf-internal-trouble:latest  "${CHALLENGES_ROOT}/internal_trouble"
docker build -t local/ctf-lantern-registry:latest  "${CHALLENGES_ROOT}/lantern_registry"
docker build -t local/ctf-maze:latest              "${CHALLENGES_ROOT}/maze"
docker build -t local/ctf-network-archive-portal:latest "${CHALLENGES_ROOT}/network_archive_portal"

echo ""
echo "======================================================================"
echo "[SUCCESS] All images built successfully!"
echo ""
echo "Images ready:"
docker images | grep "local/ctf" | awk '{print "  "$1":"$2}'
echo "======================================================================"
