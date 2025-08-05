"""
Enhanced Configuration Manager for Ghana Inventory Recommendation System

Handles loading and validation of market data with quarterly business intelligence.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models.market_data import (
    HolidayPeriod, RegionData, ProductData, 
    ScoringWeights, BusinessParameters, EconomicFactors, QuarterData
)
from .utils.validators import DataValidator


class ConfigManager:
    """Enhanced configuration manager with quarterly business intelligence."""
    
    def __init__(self, config_path: Path):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self._raw_data: Dict[str, Any] = {}
        self._holiday_periods: Dict[str, HolidayPeriod] = {}
        self._regions: Dict[str, RegionData] = {}
        self._products: Dict[str, ProductData] = {}
        self._scoring_weights: ScoringWeights = None
        self._business_parameters: BusinessParameters = None
        
        self._load_configuration()
        self._validate_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration data from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._raw_data = json.load(file)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")
    
    def _validate_configuration(self) -> None:
        """Validate and parse configuration data into structured objects."""
        validator = DataValidator()
        
        try:
            # Validate required sections
            required_sections = [
                'holiday_periods', 'regions', 'products', 
                'scoring_weights', 'business_parameters'
            ]
            
            for section in required_sections:
                if section not in self._raw_data:
                    raise ValueError(f"Missing required section: {section}")
            
            # Parse holiday periods
            self._holiday_periods = {}
            for name, data in self._raw_data['holiday_periods'].items():
                holiday = HolidayPeriod(
                    name=name,
                    months=data['months'],
                    multiplier=data['multiplier'],
                    duration_days=data['duration_days'],
                    description=data.get('description', '')
                )
                validator.validate_holiday_period(holiday)
                self._holiday_periods[name] = holiday
            
            # Parse regions with enhanced data
            self._regions = {}
            for name, data in self._raw_data['regions'].items():
                region = RegionData(
                    name=name,
                    region_type=data['type'],
                    population=data['population'],
                    income_level=data['income_level'],
                    dominant_work=data['dominant_work'],
                    key_locations=data['key_locations'],
                    infrastructure=data['infrastructure'],
                    customer_behavior=data['customer_behavior'],
                    economic_indicators=data.get('economic_indicators', {})
                )
                validator.validate_region_data(region)
                self._regions[name] = region
            
            # Parse products with enhanced quarterly data
            self._products = {}
            for product_id, data in self._raw_data['products'].items():
                product = ProductData(
                    product_id=product_id,
                    name=data['name'],
                    category=data['category'],
                    cost_price_cedis=data['cost_price_cedis'],
                    selling_price_cedis=data['selling_price_cedis'],
                    perishability_days=data['perishability_days'],
                    typical_sale_time_days=data['typical_sale_time_days'],
                    storage_requirements=data['storage_requirements'],
                    customer_benefit=data['customer_benefit'],
                    risk_factors=data['risk_factors'],
                    seasonal_multipliers=data['seasonal_multipliers'],
                    target_demographics=data['target_demographics'],
                    location_suitability=data['location_suitability'],
                    supplier_info=data.get('supplier_info', {}),
                    # Enhanced fields
                    base_cost_usd=data.get('base_cost_usd'),
                    base_cost_cedis=data.get('base_cost_cedis'),
                    import_dependent=data.get('import_dependent', False),
                    quarterly_demand=data.get('quarterly_demand', {})
                )
                validator.validate_product_data(product)
                self._products[product_id] = product
            
            # Parse scoring weights
            weights_data = self._raw_data['scoring_weights']
            self._scoring_weights = ScoringWeights(
                profitability=weights_data['profitability'],
                demand_potential=weights_data['demand_potential'],
                risk_adjustment=weights_data['risk_adjustment'],
                infrastructure_fit=weights_data['infrastructure_fit'],
                customer_benefit=weights_data['customer_benefit']
            )
            validator.validate_scoring_weights(self._scoring_weights)
            
            # Parse business parameters
            params_data = self._raw_data['business_parameters']
            self._business_parameters = BusinessParameters(
                max_score=params_data['max_score'],
                population_normalization_factor=params_data['population_normalization_factor'],
                location_density_normalization=params_data['location_density_normalization'],
                customer_benefit_keywords=params_data['customer_benefit_keywords']
            )
            validator.validate_business_parameters(self._business_parameters)
            
            self.logger.info("Configuration validation completed successfully")
            
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    # Enhanced quarterly methods
    def get_economic_factors(self) -> EconomicFactors:
        """Get economic indicators for quarterly calculations."""
        return EconomicFactors()  # Uses defaults from dataclass
    
    def get_quarters(self) -> Dict[str, QuarterData]:
        """Get quarterly business periods."""
        return {
            'Q1': QuarterData(
                months=[1, 2, 3],
                season='dry_season_end',
                description='End of Harmattan, School resumption, Independence celebrations',
                holiday_multiplier=1.4,
                events=['New_Year', 'Independence_Day', 'Easter']
            ),
            'Q2': QuarterData(
                months=[4, 5, 6],
                season='rainy_season_start',
                description='Rainy season begins, Farming activities, Easter period',
                holiday_multiplier=1.2,
                events=['Easter', 'Mothers_Day', 'Labour_Day']
            ),
            'Q3': QuarterData(
                months=[7, 8, 9],
                season='peak_rainy_season',
                description='Peak rains, Back-to-school, Agricultural productivity',
                holiday_multiplier=1.6,
                events=['Back_to_School', 'Farmers_Day']
            ),
            'Q4': QuarterData(
                months=[10, 11, 12],
                season='dry_season_start',
                description='Dry season starts, Harvest time, Christmas celebrations',
                holiday_multiplier=1.8,
                events=['Christmas', 'New_Year_prep', 'Harvest_celebrations']
            )
        }
    
    def get_current_quarter(self) -> str:
        """Get current quarter based on current month."""
        current_month = datetime.now().month
        return f"Q{(current_month - 1) // 3 + 1}"
    
    def get_enhanced_holiday_periods(self) -> Dict[str, Dict]:
        """Enhanced holiday periods with quarterly multipliers."""
        return {
            'Q1': {'multiplier': 1.4, 'events': ['New_Year', 'Independence_Day', 'Easter']},
            'Q2': {'multiplier': 1.2, 'events': ['Easter', 'Mothers_Day', 'Labour_Day']},
            'Q3': {'multiplier': 1.6, 'events': ['Back_to_School', 'Farmers_Day']},
            'Q4': {'multiplier': 1.8, 'events': ['Christmas', 'New_Year_prep', 'Harvest_celebrations']}
        }
    
    def load_enhanced_products_from_file(self, products_file_path: Path) -> Dict[str, ProductData]:
        """Load enhanced products with quarterly data from separate file."""
        try:
            with open(products_file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            enhanced_products = {}
            for product_id, data in products_data.items():
                product = ProductData(
                    product_id=product_id,
                    name=data['name'],
                    category=data['category'],
                    cost_price_cedis=data.get('cost_price_cedis', data.get('selling_price_cedis', 0) * 0.7),  # Fallback
                    selling_price_cedis=data['selling_price_cedis'],
                    perishability_days=data['perishability_days'],
                    typical_sale_time_days=data['typical_sale_time_days'],
                    storage_requirements=data.get('storage_requirements', ['dry']),
                    customer_benefit=data['customer_benefit'],
                    risk_factors=data.get('risk_factors', []),
                    seasonal_multipliers=data.get('seasonal_multipliers', {}),
                    target_demographics=data.get('target_demographics', []),
                    location_suitability=data['location_suitability'],
                    supplier_info=data.get('supplier_info', {}),
                    # Enhanced quarterly fields
                    base_cost_usd=data.get('base_cost_usd'),
                    base_cost_cedis=data.get('base_cost_cedis'),
                    import_dependent=data.get('import_dependent', False),
                    quarterly_demand=data.get('quarterly_demand', {
                        'Q1': 1.0, 'Q2': 1.0, 'Q3': 1.0, 'Q4': 1.0
                    })
                )
                enhanced_products[product_id] = product
            
            self.logger.info(f"Loaded {len(enhanced_products)} enhanced products")
            return enhanced_products
            
        except Exception as e:
            self.logger.error(f"Error loading enhanced products: {e}")
            return {}
    
    # Existing methods with enhancements
    def get_holiday_periods(self) -> Dict[str, HolidayPeriod]:
        """Get all holiday periods."""
        return self._holiday_periods.copy()
    
    def get_holiday_period(self, name: str) -> Optional[HolidayPeriod]:
        """Get a specific holiday period by name."""
        return self._holiday_periods.get(name)
    
    def get_regions(self) -> Dict[str, RegionData]:
        """Get all regions."""
        return self._regions.copy()
    
    def get_region(self, name: str) -> Optional[RegionData]:
        """Get a specific region by name."""
        return self._regions.get(name)
    
    def get_products(self) -> Dict[str, ProductData]:
        """Get all products."""
        return self._products.copy()
    
    def get_product(self, product_id: str) -> Optional[ProductData]:
        """Get a specific product by ID."""
        return self._products.get(product_id)
    
    def get_scoring_weights(self) -> ScoringWeights:
        """Get scoring weights configuration."""
        return self._scoring_weights
    
    def get_business_parameters(self) -> BusinessParameters:
        """Get business parameters configuration."""
        return self._business_parameters
    
    def get_products_by_category(self, category: str) -> List[ProductData]:
        """Get all products in a specific category."""
        return [
            product for product in self._products.values()
            if product.category == category
        ]
    
    def get_products_by_quarter_performance(self, quarter: str, threshold: float = 1.2) -> List[ProductData]:
        """Get products that perform well in a specific quarter."""
        return [
            product for product in self._products.values()
            if product.quarterly_demand.get(quarter, 1.0) >= threshold
        ]
    
    def get_imported_products(self) -> List[ProductData]:
        """Get all import-dependent products."""
        return [
            product for product in self._products.values()
            if product.import_dependent
        ]
    
    def get_local_products(self) -> List[ProductData]:
        """Get all locally-sourced products."""
        return [
            product for product in self._products.values()
            if not product.import_dependent
        ]
    
    def get_regions_by_type(self, region_type: str) -> List[RegionData]:
        """Get all regions of a specific type."""
        return [
            region for region in self._regions.values()
            if region.region_type == region_type
        ]
    
    def get_seasonal_products(self, season: str) -> List[ProductData]:
        """Get products that are seasonal for a specific period."""
        seasonal_products = []
        for product in self._products.values():
            for seasonal_event, multiplier in product.seasonal_multipliers.items():
                if season.lower() in seasonal_event.lower() and multiplier > 1.2:
                    seasonal_products.append(product)
                    break
        return seasonal_products
    
    def reload_configuration(self) -> None:
        """Reload configuration from file."""
        self.logger.info("Reloading configuration...")
        self._load_configuration()
        self._validate_configuration()
        self.logger.info("Configuration reloaded successfully")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded configuration."""
        return {
            'config_file': str(self.config_path),
            'last_loaded': self.config_path.stat().st_mtime,
            'holiday_periods_count': len(self._holiday_periods),
            'regions_count': len(self._regions),
            'products_count': len(self._products),
            'regions': list(self._regions.keys()),
            'product_categories': list(set(p.category for p in self._products.values())),
            'scoring_weights': self._scoring_weights.__dict__,
            'business_parameters': self._business_parameters.__dict__,
            # Enhanced summary
            'imported_products_count': len(self.get_imported_products()),
            'local_products_count': len(self.get_local_products()),
            'current_quarter': self.get_current_quarter(),
            'economic_factors': self.get_economic_factors().__dict__
        }
    
    def export_enhanced_products_template(self, output_path: Path) -> None:
        """Export a template for enhanced products with quarterly data."""
        template = {
            "product_id_example": {
                "name": "Product Name",
                "category": "category_name",
                "selling_price_cedis": 100.0,
                "perishability_days": 365,
                "typical_sale_time_days": 30,
                "customer_benefit": "Product benefits description",
                "location_suitability": {
                    "urban_coastal": 1.2,
                    "urban_inland": 1.0,
                    "urban_northern": 0.9,
                    "coastal_tourism": 1.1
                },
                # Enhanced quarterly fields
                "base_cost_usd": 5.0,  # For imported goods
                "base_cost_cedis": 75.0,  # For local goods  
                "import_dependent": True,
                "quarterly_demand": {
                    "Q1": 1.1,
                    "Q2": 1.0,
                    "Q3": 1.3,
                    "Q4": 1.6
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Enhanced products template exported to {output_path}")
    
    def validate_quarterly_data_completeness(self) -> Dict[str, List[str]]:
        """Validate that all products have complete quarterly data."""
        issues = {
            'missing_quarterly_demand': [],
            'missing_cost_data': [],
            'incomplete_location_suitability': []
        }
        
        required_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        required_location_types = ['urban_coastal', 'urban_inland', 'urban_northern', 'coastal_tourism']
        
        for product_id, product in self._products.items():
            # Check quarterly demand
            missing_quarters = [q for q in required_quarters if q not in product.quarterly_demand]
            if missing_quarters:
                issues['missing_quarterly_demand'].append(f"{product_id}: {missing_quarters}")
            
            # Check cost data
            if not product.base_cost_usd and not product.base_cost_cedis:
                issues['missing_cost_data'].append(product_id)
            
            # Check location suitability
            missing_locations = [loc for loc in required_location_types 
                               if loc not in product.location_suitability]
            if missing_locations:
                issues['incomplete_location_suitability'].append(f"{product_id}: {missing_locations}")
        
        return issues