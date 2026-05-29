#!/bin/bash
# Verify that no sensitive data is exposed in the GitHub-ready package

echo "🔍 Sanitization Verification Script"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# Check for IP addresses (private)
echo "Checking for private IP addresses..."
if grep -r "192\.168\." --include="*.md" --include="*.py" --include="*.sh" . 2>/dev/null | grep -v "EXAMPLE\|example\|placeholder"; then
    echo -e "${RED}✗ Found private IP addresses${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No private IP addresses${NC}"
fi
echo ""

# Check for hardcoded usernames (eric)
echo "Checking for hardcoded usernames..."
if grep -r "eric@\|eric " --include="*.md" --include="*.py" --include="*.sh" . 2>/dev/null | grep -v "EXAMPLE\|example"; then
    echo -e "${RED}✗ Found hardcoded usernames${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No hardcoded usernames${NC}"
fi
echo ""

# Check for email addresses
echo "Checking for email addresses..."
if grep -r "[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]*\.[a-zA-Z]*" --include="*.md" --include="*.py" --include="*.sh" . 2>/dev/null | grep -v "example\|EXAMPLE\|your\|yourusername" | head -5; then
    echo -e "${YELLOW}⚠ Check email addresses above (may be examples)${NC}"
else
    echo -e "${GREEN}✓ No exposed email addresses${NC}"
fi
echo ""

# Check for API keys
echo "Checking for API keys..."
if grep -r "api.key\|api_key.*=\|API_KEY.*=\|secret.*=" --include="*.py" . 2>/dev/null | grep -v "no-key\|example\|EXAMPLE" | head -5; then
    echo -e "${RED}✗ Found potential API keys${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No API keys${NC}"
fi
echo ""

# Check for passwords
echo "Checking for passwords..."
if grep -r "password\|passwd" --include="*.py" --include="*.md" . 2>/dev/null | grep -v "# password\|example\|EXAMPLE"; then
    echo -e "${RED}✗ Found potential passwords${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No passwords${NC}"
fi
echo ""

# Check for AWS keys
echo "Checking for AWS credentials..."
if grep -r "AKIA\|aws_access_key\|aws_secret" --include="*.py" --include="*.md" . 2>/dev/null; then
    echo -e "${RED}✗ Found AWS credentials${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No AWS credentials${NC}"
fi
echo ""

# Check for .env files
echo "Checking for .env files..."
if find . -name ".env*" ! -path "./venv/*" -type f 2>/dev/null; then
    echo -e "${RED}✗ Found .env files${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No .env files${NC}"
fi
echo ""

# Check for local paths
echo "Checking for local machine paths..."
if grep -r "/home/\|/Users/\|/root/\|C:\\\\Users" --include="*.md" --include="*.py" --include="*.sh" . 2>/dev/null | grep -v "example\|EXAMPLE\|<" | head -3; then
    echo -e "${YELLOW}⚠ Check paths above (may be examples)${NC}"
else
    echo -e "${GREEN}✓ No hardcoded local paths${NC}"
fi
echo ""

# Check for git status
echo "Checking for git status..."
if git status 2>/dev/null | grep -q "nothing to commit"; then
    echo -e "${GREEN}✓ All changes committed${NC}"
else
    echo -e "${YELLOW}⚠ Uncommitted changes exist${NC}"
fi
echo ""

# Summary
echo "===================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ Sanitization Complete - Ready for GitHub!${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ISSUES_FOUND issue(s)${NC}"
    exit 1
fi
