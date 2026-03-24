#!/bin/bash
# test.sh - Verification rapide du projet avant commit
set -uo pipefail

R='\033[0;31m' G='\033[0;32m' Y='\033[0;33m' B='\033[0;34m' N='\033[0m'
ERR=0 WRN=0

ok()   { echo -e "${G}  +${N} $1"; }
warn() { echo -e "${Y}  !${N} $1"; WRN=$((WRN+1)); }
fail() { echo -e "${R}  x${N} $1"; ERR=$((ERR+1)); }
hdr()  { echo -e "\n${B}-- $1 --${N}"; }

echo "======================================"
echo "  TAWIZA - Tests projet"
echo "======================================"

# --- SECURITE ---
hdr "SECURITE"

S=$(grep -rn -E '(api[_-]?key|token|secret|password|Bearer)\s*[:=]\s*["'"'"'][A-Za-z0-9+/=_-]{20,}' \
  --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.json" --include="*.yml" \
  --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir=".venv" \
  --exclude=".env.example" --exclude="pyproject.toml" --exclude="*.lock" . 2>/dev/null || true)
[ -z "$S" ] && ok "Aucun secret detecte" || fail "Secrets potentiels detectes"

F=$(find . -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" \
  \( -name "*.env" -not -name ".env.example" -not -name ".env.local.example" \) \
  -o -name "*.secret" -o -name "*.key" -o -name "*.pem" -o -name "id_rsa*" 2>/dev/null)
[ -z "$F" ] && ok "Pas de fichier sensible" || fail "Fichiers sensibles : $F"

P=$(grep -rn 'MPtoO-V2\|hamidedefr\|moltbot-secure' \
  --include="*.py" --include="*.ts" --include="*.tsx" --include="*.md" \
  --exclude-dir=".git" --exclude-dir="node_modules" --exclude="CLAUDE.md" --exclude="AUDIT.md" . 2>/dev/null || true)
[ -z "$P" ] && ok "Pas de reference au repo prive" || warn "References au repo prive trouvees"

# --- HUMANISATION ---
hdr "HUMANISATION"

EM=$(find . -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" \
  \( -name "*.md" -o -name "*.py" \) -exec grep -l $'\xe2\x80\x94' {} + 2>/dev/null | wc -l)
[ "$EM" -eq 0 ] && ok "Aucun em dash" || warn "$EM fichiers avec em dashes"

AI=$(grep -rci -E 'comprehensive|seamless|leverage|cutting-edge|state-of-the-art|delve into' \
  --include="*.md" --exclude-dir=".git" --exclude="CLAUDE.md" --exclude="AUDIT.md" . 2>/dev/null \
  | awk -F: '{s+=$2}END{print s+0}')
[ "$AI" -eq 0 ] && ok "Pas de vocabulaire AI dans les .md" || warn "$AI mots AI dans la doc"

CL=$(git log --all --format='%b' 2>/dev/null | grep -ci 'Co-Authored-By.*[Cc]laude\|Co-Authored-By.*anthropic')
[ "$CL" -eq 0 ] && ok "Pas de Co-Authored-By Claude" || fail "$CL references Claude dans l'historique"

# --- FICHIERS OBLIGATOIRES ---
hdr "FICHIERS PROJET"

for f in README.md LICENSE SECURITY.md CONTRIBUTING.md .gitignore ROADMAP.md CHANGELOG.md; do
  [ -f "$f" ] && ok "$f" || fail "$f MANQUANT"
done

# --- STRUCTURE ---
hdr "STRUCTURE"

[ -d "src/" ] && ok "src/ present ($(find src/ -name '*.py' | wc -l) fichiers Python)" || fail "src/ manquant"
[ -d "frontend/" ] && ok "frontend/ present ($(find frontend/ -name '*.tsx' -o -name '*.ts' | wc -l) fichiers TS)" || fail "frontend/ manquant"
[ -d "tests/" ] && ok "tests/ present ($(find tests/ -name 'test_*.py' | wc -l) fichiers de test)" || fail "tests/ manquant"
[ -f "pyproject.toml" ] && ok "pyproject.toml" || fail "pyproject.toml manquant"
[ -f "docker-compose.yml" ] && ok "docker-compose.yml" || fail "docker-compose.yml manquant"

# Verifier les 7 pages dashboard
PAGES=$(ls -d frontend/app/dashboard/*/ 2>/dev/null | wc -l)
[ "$PAGES" -eq 7 ] && ok "Dashboard : $PAGES pages (correct)" || warn "Dashboard : $PAGES pages (attendu 7)"

# --- POIDS ---
hdr "POIDS"

HVY=$(find . -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" \
  \( -name "*.jpg" -o -name "*.png" -o -name "*.gif" \) -size +500k 2>/dev/null | wc -l)
[ "$HVY" -eq 0 ] && ok "Pas d'image trop lourde (>500KB)" || warn "$HVY images > 500KB"

BIG=$(find . -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" \
  -not -path "./htmlcov/*" -name "*.py" -size +100k 2>/dev/null)
if [ -n "$BIG" ]; then
  warn "Fichiers Python > 100KB :"
  echo "$BIG" | while read f; do echo "      $(du -h "$f" | cut -f1) $f"; done
fi

# --- RESUME ---
echo ""
echo "======================================"
if [ "$ERR" -gt 0 ]; then
  echo -e "  ${R}ECHEC${N} - $ERR erreurs, $WRN avertissements"
  exit 1
elif [ "$WRN" -gt 0 ]; then
  echo -e "  ${Y}ATTENTION${N} - 0 erreurs, $WRN avertissements"
  exit 0
else
  echo -e "  ${G}TOUT EST BON${N}"
  exit 0
fi
