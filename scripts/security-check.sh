#!/bin/bash
# Security verification script
# Checks if critical security fixes are applied

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "MPtoO-V2 Security Verification"
echo "================================================"
echo ""

PASSED=0
FAILED=0

# Function to check test
check() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Checking: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
    fi
}

# 1. Check if secrets are removed from Git
check "Secrets removed from Git" \
    "! git log --all --full-history -p -- .env 2>/dev/null | grep -q 'PASSWORD='"

# 2. Check if .env is in .gitignore
check ".env in .gitignore" \
    "grep -q '^\.env$' .gitignore"

# 3. Check if authentication module exists
check "Authentication module exists" \
    "test -f src/infrastructure/security/auth.py"

# 4. Check if input validation exists
check "Input validation implemented" \
    "grep -q 'validate_model_name' src/infrastructure/ml/fine_tuning/fine_tuning_service.py"

# 5. Check if SSRF protection exists
check "SSRF protection module exists" \
    "test -f src/infrastructure/security/url_validation.py"

# 6. Check if security headers are configured
check "Security headers middleware exists" \
    "test -f src/infrastructure/middleware/security_headers.py || grep -q 'X-Frame-Options' src/interfaces/api/main.py"

# 7. Check if rate limiting is configured
check "Rate limiting configured" \
    "grep -q 'slowapi\|Limiter' src/interfaces/api/main.py"

# 8. Check if debug mode is disabled
check "Debug mode disabled" \
    "! grep -q 'DEBUG=true' .env"

# 9. Check if JWT dependencies are installed
check "JWT dependencies installed" \
    "pip show pyjwt > /dev/null 2>&1"

# 10. Check if security tests exist
check "Security tests exist" \
    "test -d tests/security || test -f tests/security/test_auth.py"

echo ""
echo "================================================"
echo -e "Results: ${GREEN}${PASSED} PASSED${NC} | ${RED}${FAILED} FAILED${NC}"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical security checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some security checks failed. Review and fix before production.${NC}"
    echo ""
    echo "See documentation:"
    echo "  - SECURITY-FIXES-QUICK-START.md (implementation guide)"
    echo "  - SECURITY-AUDIT-REPORT.md (detailed vulnerabilities)"
    exit 1
fi
