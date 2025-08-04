# Ghana Inventory Recommendation System

A comprehensive business intelligence tool that provides data-driven inventory recommendations for the Ghanaian market. This system analyzes multiple factors including profitability, demand potential, risk assessment, and infrastructure compatibility to help businesses make informed inventory decisions.

## 🏆 Features

- **Business-Focused Analysis**: Comprehensive scoring based on profitability, demand, risk, and infrastructure
- **Regional Intelligence**: Detailed analysis for major Ghanaian cities (Accra, Kumasi, Tamale, Cape Coast)
- **Seasonal Optimization**: Holiday and seasonal demand pattern analysis
- **Risk Assessment**: Infrastructure compatibility and business risk evaluation
- **Multiple Export Formats**: Console, JSON, and CSV output options
- **Modular Architecture**: Professional, maintainable codebase with clear separation of concerns

## 🗂️ Project Structure

```
ghana-inventory-recommender/
├── main.py                          # Application entry point
├── data/
│   └── ghana_market_data.json      # Market data configuration
├── src/
│   ├── __init__.py
│   ├── config_manager.py           # Configuration management
│   ├── inventory_recommender.py    # Main recommender class
│   ├── models/
│   │   ├── __init__.py
│   │   └── market_data.py          # Data models and structures
│   ├── calculators/
│   │   ├── __init__.py
│   │   └── business_score_calculator.py  # Business scoring logic
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Logging utilities
│       ├── validators.py           # Data validation
│       └── formatters.py           # Output formatting
├── logs/                           # Application logs (auto-created)
├── output/                         # Export files (auto-created)
├── requirements.txt                # Python dependencies
├── setup.py                       # Package setup
└── README.md                       # This file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ghana-inventory-recommender
```

2. **Install dependencies** (optional - no external dependencies required):
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python main.py --locations Accra Kumasi
```

### Basic Usage

```bash
# Get recommendations for specific locations
python main.py --locations Accra Kumasi

# Analyze for a specific month (Christmas season)
python main.py --locations Accra --month 12

# Export to JSON
python main.py --locations "Cape Coast" --format json --output results.json

# Export to CSV with custom number of recommendations
python main.py --locations Tamale --recommendations 10 --format csv
```

## 📊 Configuration

The system uses a comprehensive JSON configuration file (`data/ghana_market_data.json`) that contains:

### Holiday Periods
- Christmas season, Easter, Independence Day, Farmers Day, Back-to-school periods
- Each with specific months, demand multipliers, and duration

### Regional Data
- **Accra**: Urban coastal, high income, 2.4M population
- **Kumasi**: Urban inland, medium-high income, 3.3M population  
- **Tamale**: Urban northern, medium income, 950K population
- **Cape Coast**: Coastal tourism, medium income, 230K population

Each region includes:
- Demographics and economic indicators
- Infrastructure metrics (electricity, storage, transport)
- Customer behavior patterns
- Key location counts (churches, schools, companies, etc.)

### Product Portfolio
- **Staple Foods**: Imported rice, local palm oil
- **Protein**: Canned sardines
- **Telecommunications**: Mobile phone credit
- **Energy Solutions**: Solar lanterns
- **Cultural Goods**: Kente accessories
- **Education**: Basic school supplies
- **Health Products**: Treated mosquito nets

Each product includes:
- Pricing and profitability data
- Storage requirements and perishability
- Target demographics and benefits
- Risk factors and supplier information
- Location suitability by region type

## 🧮 Business Scoring Algorithm

The system uses a weighted scoring algorithm with five components:

1. **Profitability (35%)**: Profit margins, sale velocity, income compatibility
2. **Demand Potential (30%)**: Population factors, location fit, seasonal boosts
3. **Risk Adjustment (20%)**: Perishability, storage compatibility, risk factors
4. **Infrastructure Fit (10%)**: Storage requirements vs. available infrastructure
5. **Customer Benefit (5%)**: Alignment with customer needs and benefits

## 📈 Output Formats

### Console Output
Rich, formatted recommendations with:
- Business scores and rankings
- Financial projections (revenue/profit)
- Customer benefits and risk factors
- Detailed analysis reasoning

### JSON Export
Structured data export including:
- Metadata and analysis parameters
- Region information and demographics
- Complete recommendation details
- Financial projections and scoring breakdown

### CSV Export
Tabular format suitable for spreadsheet analysis:
- One row per recommendation
- All key metrics and projections
- Filterable and sortable data

## 🛠️ Advanced Usage

### Custom Configuration
Modify `data/ghana_market_data.json` to:
- Add new products or regions
- Update pricing and market data
- Adjust scoring weights and parameters
- Include new holiday periods or demographics

### Programmatic Usage
```python
from src.config_manager import ConfigManager
from src.inventory_recommender import GhanaInventoryRecommender

# Initialize system
config = ConfigManager('data/ghana_market_data.json')
recommender = GhanaInventoryRecommender(config)

# Get recommendations
recommendations = recommender.get_recommendations('Accra', 5, 12)

# Location comparison
comparison = recommender.compare_locations(['Accra', 'Kumasi'])
```

### Logging and Debugging
```bash
# Enable debug logging
python main.py --locations Accra --log-level DEBUG

# Logs are automatically saved to logs/ directory
```

## 🔧 Development

### Code Quality
The system follows professional development practices:
- **Type Hints**: Full type annotation throughout
- **Modular Design**: Clear separation of concerns
- **Data Validation**: Comprehensive input validation
- **Error Handling**: Robust error handling and logging
- **Documentation**: Comprehensive docstrings and comments

### Testing
```bash
# Run tests (when implemented)
python -m pytest tests/

# Code formatting
black src/ main.py

# Linting
flake8 src/ main.py
```

### Extending the System

#### Adding New Regions
1. Add region data to `ghana_market_data.json`
2. Include infrastructure and demographic data
3. Update product location suitability mappings

#### Adding New Products
1. Define product in the JSON configuration
2. Include pricing, storage, and demographic data
3. Set location suitability multipliers
4. Define seasonal demand patterns

#### Customizing Scoring
1. Modify scoring weights in the configuration
2. Extend `BusinessScoreCalculator` for new metrics
3. Update validation rules as needed

## 📋 Business Use Cases

### Retail Chain Planning
- Optimize inventory across multiple locations
- Seasonal demand planning and preparation
- New location market entry analysis

### Small Business Optimization
- Product selection for maximum profitability
- Risk assessment for inventory investments
- Market timing for product launches

### Market Research
- Regional market opportunity analysis
- Competitive product positioning
- Infrastructure impact assessment

## 🎯 Key Business Insights

The system provides actionable insights such as:
- **High-margin opportunities** in specific regions
- **Seasonal timing** for maximum profitability
- **Infrastructure requirements** for product success
- **Risk mitigation** strategies for inventory planning
- **Market entry** recommendations for new locations

## 📞 Support

For questions, issues, or contributions:
1. Check the documentation in the codebase
2. Review the JSON configuration format
3. Examine the scoring algorithm implementation
4. Test with different scenarios and parameters

## 📄 License

This project is developed for the Kola Market take-home challenge and demonstrates professional software engineering practices for business intelligence applications.
