#!/usr/bin/env bash
# =============================================================================
# MPtoO-V2 - Tailscale Dashboard Manager
# Active/desactive le portail MPtoO via Tailscale
#
# Usage:
#   ./scripts/tailscale-dashboard.sh start   # Activer le dashboard
#   ./scripts/tailscale-dashboard.sh stop    # Desactiver
#   ./scripts/tailscale-dashboard.sh status  # Voir le status
#   ./scripts/tailscale-dashboard.sh url     # Afficher l'URL d'acces
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

NGINX_PORT=8443
DASHBOARD_SRC="/root/MPtoO-V2/docker/nginx/dashboard.html"
DASHBOARD_DEST="/var/www/mptoo-dashboard/dashboard.html"
NGINX_CONF="/etc/nginx/sites-available/mptoo-tailscale"
NGINX_LINK="/etc/nginx/sites-enabled/mptoo-tailscale"

TS_HOSTNAME=$(tailscale status --self --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('DNSName','').rstrip('.'))" 2>/dev/null || echo "unknown")

case "${1:-status}" in
    start)
        echo -e "${BOLD}${BLUE}Starting MPtoO Tailscale Dashboard...${NC}"
        echo ""

        # 1. Sync dashboard HTML
        if [[ -f "$DASHBOARD_SRC" ]]; then
            mkdir -p "$(dirname "$DASHBOARD_DEST")"
            cp "$DASHBOARD_SRC" "$DASHBOARD_DEST"
            chmod 644 "$DASHBOARD_DEST"
            echo -e "  ${GREEN}[OK]${NC} Dashboard HTML synced"
        else
            echo -e "  ${RED}[FAIL]${NC} Dashboard source not found: $DASHBOARD_SRC"
            exit 1
        fi

        # 2. Enable nginx site
        if [[ -f "$NGINX_CONF" ]]; then
            ln -sf "$NGINX_CONF" "$NGINX_LINK"
            nginx -t 2>/dev/null && systemctl reload nginx
            echo -e "  ${GREEN}[OK]${NC} Nginx config enabled and reloaded"
        else
            echo -e "  ${RED}[FAIL]${NC} Nginx config not found: $NGINX_CONF"
            exit 1
        fi

        # 3. Verify nginx listens
        sleep 1
        if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${NGINX_PORT}/" 2>/dev/null | grep -q "200"; then
            echo -e "  ${GREEN}[OK]${NC} Nginx listening on 127.0.0.1:${NGINX_PORT}"
        else
            echo -e "  ${YELLOW}[WARN]${NC} Nginx returned non-200 on port ${NGINX_PORT}"
        fi

        # 4. Configure tailscale serve
        tailscale serve reset 2>/dev/null || true
        tailscale serve --bg "${NGINX_PORT}" 2>/dev/null
        echo -e "  ${GREEN}[OK]${NC} Tailscale serve configured (tailnet only)"

        echo ""
        echo -e "${BOLD}${GREEN}Dashboard active!${NC}"
        echo -e "  URL: ${CYAN}https://${TS_HOSTNAME}/${NC}"
        echo ""
        echo -e "  Accessible depuis tous tes appareils Tailscale:"
        tailscale status 2>/dev/null | grep -v "^$" | head -15 | while read -r line; do
            echo -e "    ${line}"
        done
        ;;

    stop)
        echo -e "${BOLD}${BLUE}Stopping MPtoO Tailscale Dashboard...${NC}"

        # Remove tailscale serve
        tailscale serve reset 2>/dev/null || true
        echo -e "  ${GREEN}[OK]${NC} Tailscale serve reset"

        # Disable nginx site (but keep config)
        rm -f "$NGINX_LINK"
        nginx -t 2>/dev/null && systemctl reload nginx
        echo -e "  ${GREEN}[OK]${NC} Nginx site disabled"

        echo ""
        echo -e "${YELLOW}Dashboard stopped.${NC} Run '$0 start' to reactivate."
        ;;

    status)
        echo -e "${BOLD}${BLUE}MPtoO Tailscale Dashboard Status${NC}"
        echo ""

        # Tailscale status
        echo -e "${CYAN}Tailscale Serve:${NC}"
        tailscale serve status 2>&1 | while read -r line; do
            echo "  $line"
        done

        echo ""
        echo -e "${CYAN}Nginx (port ${NGINX_PORT}):${NC}"
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${NGINX_PORT}/" 2>/dev/null || echo "000")
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo -e "  ${GREEN}[OK]${NC} Serving on 127.0.0.1:${NGINX_PORT} (HTTP $HTTP_CODE)"
        elif [[ "$HTTP_CODE" == "000" ]]; then
            echo -e "  ${RED}[DOWN]${NC} Not responding on port ${NGINX_PORT}"
        else
            echo -e "  ${YELLOW}[WARN]${NC} HTTP $HTTP_CODE on port ${NGINX_PORT}"
        fi

        echo ""
        echo -e "${CYAN}HTTPS via Tailscale:${NC}"
        TS_CODE=$(curl -sk -o /dev/null -w "%{http_code}" "https://${TS_HOSTNAME}/" 2>/dev/null || echo "000")
        if [[ "$TS_CODE" == "200" ]]; then
            echo -e "  ${GREEN}[OK]${NC} https://${TS_HOSTNAME}/ (HTTP $TS_CODE)"
        elif [[ "$TS_CODE" == "000" ]]; then
            echo -e "  ${RED}[DOWN]${NC} https://${TS_HOSTNAME}/ not reachable"
        else
            echo -e "  ${YELLOW}[WARN]${NC} https://${TS_HOSTNAME}/ (HTTP $TS_CODE)"
        fi
        ;;

    url)
        echo "https://${TS_HOSTNAME}/"
        ;;

    *)
        echo "Usage: $0 {start|stop|status|url}"
        exit 1
        ;;
esac
