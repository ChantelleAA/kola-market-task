#!/bin/bash

echo "🇬🇭 Ghana Inventory Recommendation System - Setup Script"
echo "==========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python is installed
print_header "🐍 Checking Python Installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
else
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

# Create project directory structure
print_header "📁 Creating Project Structure..."

# Create main directories
mkdir -p src/{models,calculators,utils,api}
mkdir -p web/{templates,static/{css,js,images}}
mkdir -p data
mkdir -p logs
mkdir -p output
mkdir -p tests

print_status "Directory structure created"

# Create __init__.py files
touch src/__init__.py
touch src/models/__init__.py
touch src/calculators/__init__.py
touch src/utils/__init__.py
touch src/api/__init__.py
touch tests/__init__.py

print_status "Python package files created"

# Install dependencies
print_header "📦 Installing Dependencies..."
pip3 install Flask Flask-CORS

print_status "Dependencies installed successfully"

# Create a simple start script
print_header "🚀 Creating Start Scripts..."

# CLI start script
cat > start_cli.sh << 'EOF'
#!/bin/bash
echo "🇬🇭 Starting Ghana Inventory CLI..."
python3 main.py "$@"
EOF

# Web start script
cat > start_web.sh << 'EOF'
#!/bin/bash
echo "🇬🇭 Starting Ghana Inventory Web Dashboard..."
echo "Dashboard will be available at: http://localhost:5000"
python3 app.py
EOF

# Make scripts executable
chmod +x start_cli.sh
chmod +x start_web.sh

print_status "Start scripts created"

# Create sample data file if it doesn't exist
if [ ! -f "data/ghana_market_data.json" ]; then
    print_header "📊 Creating Sample Data File..."
    cat > data/ghana_market_data.json << 'EOF'
{
  "holiday_periods": {
    "christmas_season": {
      "months": [11, 12],
      "multiplier": 1.8,
      "duration_days": 60,
      "description": "Christmas and New Year celebrations"
    }
  },
  "regions": {
    "Accra": {
      "type": "urban_coastal",
      "population": 2400000,
      "income_level": "high",
      "dominant_work": ["office_workers", "traders"],
      "key_locations": {"churches": 450, "schools": 280},
      "infrastructure": {"electricity_reliability": 0.85, "cold_storage_access": 0.7, "transport_quality": 0.8},
      "customer_behavior": {"impulse_buying": 0.8, "brand_consciousness": 0.9, "price_sensitivity": 0.6}
    }
  },
  "products": {
    "mobile_phone_credit": {
      "category": "telecommunications",
      "name": "Mobile Phone Credit",
      "cost_price_cedis": 95.0,
      "selling_price_cedis": 100.0,
      "perishability_days": 0,
      "typical_sale_time_days": 1,
      "storage_requirements": ["digital"],
      "customer_benefit": "Essential communication",
      "risk_factors": ["network_issues"],
      "seasonal_multipliers": {"normal": 1.0},
      "target_demographics": ["everyone"],
      "location_suitability": {"urban_coastal": 1.2}
    }
  },
  "scoring_weights": {
    "profitability": 0.35,
    "demand_potential": 0.30,
    "risk_adjustment": 0.20,
    "infrastructure_fit": 0.10,
    "customer_benefit": 0.05
  },
  "business_parameters": {
    "max_score": 10.0,
    "population_normalization_factor": 500000,
    "location_density_normalization": 100,
    "customer_benefit_keywords": ["essential", "affordable", "convenient"]
  }
}
EOF
    print_status "Sample data file created"
fi

print_header "✅ Setup Complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. For CLI mode: ./start_cli.sh --locations Accra"
echo "2. For Web Dashboard: ./start_web.sh"
echo "3. Then open: http://localhost:5000"
echo ""
echo "📁 Project Structure:"
echo "├── main.py              # CLI application"
echo "├── app.py               # Web server"
echo "├── data/                # Configuration data"
echo "├── src/                 # Source code"
echo "├── web/                 # Web dashboard files"
echo "├── logs/                # Application logs"
echo "└── output/              # Export files"
echo ""
echo "🔧 Customization:"
echo "• Edit data/ghana_market_data.json to modify market data"
echo "• Add new regions, products, or adjust scoring weights"
echo "• Check logs/ directory for debugging information"
echo ""
print_status "Setup completed successfully!"