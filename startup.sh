#!/usr/bin/env bash
# Startup script for Smart SMS Authentication Module
# Run this script to quickly set up and start the development server

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Smart SMS - Authentication Module${NC}"
echo -e "${BLUE}Setup & Run Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Check Python
echo -e "\n${BLUE}[1/5]${NC} Checking Python installation..."
python --version || python3 --version || { echo "Python not found!"; exit 1; }

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "\n${BLUE}[2/5]${NC} Creating virtual environment..."
    python -m venv venv || python3 -m venv venv
else
    echo -e "\n${BLUE}[2/5]${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n${BLUE}[3/5]${NC} Installing dependencies..."
. venv/bin/activate
pip install -r requirements.txt

# Run migrations
echo -e "\n${BLUE}[4/5]${NC} Running database migrations..."
python manage.py migrate

# Create superuser info
echo -e "\n${BLUE}[5/5]${NC} Creating superuser (if not exists)..."
python manage.py createsuperuser --noinput --username "+1234567890" --email "admin@example.com" 2>/dev/null || echo "Superuser might already exist"

# Start server
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${BLUE}Starting development server...${NC}\n"
python manage.py runserver
