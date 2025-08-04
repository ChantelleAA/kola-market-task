"""
Data validation utilities for the Ghana Inventory Recommendation System.

Provides comprehensive validation for all data models and business rules.
"""

import logging
from typing import List, Dict, Any

from ..models.market_data import (
    HolidayPeriod, RegionData, ProductData, 
    ScoringWeights, BusinessParameters
)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataValidator:
    """Validates data models and business rules."""
    
    def __init__(self):
        """Initialize the validator."""
        self.logger = logging.getLogger(__name__)
        
        # Define valid values for categorical data
        self.valid_income_levels = ['low', 'medium', 'medium-high', 'high']
        self.valid_region_types = ['urban_coastal', 'urban_inland', 'urban_northern', 'coastal_tourism']
        self.valid_product_categories = [
            'staple_food', 'protein', 'telecommunications', 'energy_solutions',
            'cultural_goods', 'education', 'health_products', 'cooking_essentials'
        ]
        self.valid_storage_requirements = [
            'dry', 'cool', 'cold', 'room_temperature', 'sealed', 'digital',
            'protected_from_impact', 'protected_from_dust', 'organized_display',
            'pest_control', 'dark', 'packaged', 'organized', 'pest_free'
        ]
    
    def validate_holiday_period(self, holiday: HolidayPeriod) -> None:
        """Validate a holiday period object."""
        try:
            # Validate months
            if not holiday.months:
                raise ValidationError(f"Holiday period {holiday.name} must have at least one month")
            
            for month in holiday.months:
                if not 1 <= month <= 12:
                    raise ValidationError(f"Invalid month {month} in holiday period {holiday.name}")
            
            # Validate multiplier
            if not 0.1 <= holiday.multiplier <= 5.0:
                raise ValidationError(f"Holiday multiplier for {holiday.name} should be between 0.1 and 5.0")
            
            # Validate duration
            if not 1 <= holiday.duration_days <= 365:
                raise ValidationError(f"Holiday duration for {holiday.name} should be between 1 and 365 days")
            
            self.logger.debug(f"Holiday period {holiday.name} validated successfully")
            
        except Exception as e:
            raise ValidationError(f"Holiday period validation failed: {e}")
    
    def validate_region_data(self, region: RegionData) -> None:
        """Validate a region data object."""
        try:
            # Validate basic data
            if not region.name or not region.name.strip():
                raise ValidationError("Region name cannot be empty")
            
            if region.region_type not in self.valid_region_types:
                raise ValidationError(f"Invalid region type: {region.region_type}")
            
            if region.income_level not in self.valid_income_levels:
                raise ValidationError(f"Invalid income level: {region.income_level}")
            
            if region.population <= 0:
                raise ValidationError(f"Population must be positive for {region.name}")
            
            # Validate dominant work categories
            if not region.dominant_work:
                raise ValidationError(f"Region {region.name} must have at least one dominant work category")
            
            # Validate key locations
            required_locations = ['churches', 'schools', 'markets']
            for location in required_locations:
                if location not in region.key_locations:
                    raise ValidationError(f"Region {region.name} missing required location: {location}")
                
                if region.key_locations[location] < 0:
                    raise ValidationError(f"Location count cannot be negative for {location} in {region.name}")
            
            # Infrastructure and customer behavior are validated in their __post_init__ methods
            
            self.logger.debug(f"Region {region.name} validated successfully")
            
        except Exception as e:
            raise ValidationError(f"Region validation failed: {e}")
    
    def validate_product_data(self, product: ProductData) -> None:
        """Validate a product data object."""
        try:
            # Validate basic data
            if not product.product_id or not product.product_id.strip():
                raise ValidationError("Product ID cannot be empty")
            
            if not product.name or not product.name.strip():
                raise ValidationError(f"Product name cannot be empty for {product.product_id}")
            
            if product.category not in self.valid_product_categories:
                raise ValidationError(f"Invalid product category: {product.category}")
            
            # Validate pricing
            if product.cost_price_cedis <= 0:
                raise ValidationError(f"Cost price must be positive for {product.product_id}")
            
            if product.selling_price_cedis <= product.cost_price_cedis:
                raise ValidationError(f"Selling price must be greater than cost price for {product.product_id}")
            
            # Validate time periods
            if product.typical_sale_time_days <= 0:
                raise ValidationError(f"Sale time must be positive for {product.product_id}")
            
            if product.perishability_days < 0:
                raise ValidationError(f"Perishability days cannot be negative for {product.product_id}")
            
            # Validate storage requirements
            for requirement in product.storage_requirements:
                if requirement not in self.valid_storage_requirements:
                    self.logger.warning(f"Unknown storage requirement '{requirement}' for {product.product_id}")
            
            # Validate location suitability
            if not product.location_suitability:
                raise ValidationError(f"Product {product.product_id} must have location suitability data")
            
            for location_type, multiplier in product.location_suitability.items():
                if location_type not in self.valid_region_types:
                    raise ValidationError(f"Invalid location type in suitability: {location_type}")
                
                if not 0.1 <= multiplier <= 3.0:
                    raise ValidationError(f"Location suitability multiplier should be between 0.1 and 3.0")
            
            # Validate seasonal multipliers
            for season, multiplier in product.seasonal_multipliers.items():
                if not 0.1 <= multiplier <= 5.0:
                    raise ValidationError(f"Seasonal multiplier should be between 0.1 and 5.0")
            
            # Validate demographics and benefits
            if not product.target_demographics:
                raise ValidationError(f"Product {product.product_id} must have target demographics")
            
            if not product.customer_benefit or not product.customer_benefit.strip():
                raise ValidationError(f"Product {product.product_id} must have customer benefit description")
            
            self.logger.debug(f"Product {product.product_id} validated successfully")
            
        except Exception as e:
            raise ValidationError(f"Product validation failed: {e}")
    
    def validate_scoring_weights(self, weights: ScoringWeights) -> None:
        """Validate scoring weights configuration."""
        try:
            # Check individual weights
            weight_dict = weights.__dict__
            for name, value in weight_dict.items():
                if not 0 <= value <= 1:
                    raise ValidationError(f"Scoring weight {name} must be between 0 and 1")
            
            # Check sum
            total = sum(weight_dict.values())
            if not 0.99 <= total <= 1.01:  # Allow for floating point precision
                raise ValidationError(f"Scoring weights must sum to 1.0, got {total}")
            
            self.logger.debug("Scoring weights validated successfully")
            
        except Exception as e:
            raise ValidationError(f"Scoring weights validation failed: {e}")
    
    def validate_business_parameters(self, params: BusinessParameters) -> None:
        """Validate business parameters configuration."""
        try:
            if params.max_score <= 0:
                raise ValidationError("Max score must be positive")
            
            if params.population_normalization_factor <= 0:
                raise ValidationError("Population normalization factor must be positive")
            
            if params.location_density_normalization <= 0:
                raise ValidationError("Location density normalization must be positive")
            
            if not params.customer_benefit_keywords:
                raise ValidationError("Must have at least one customer benefit keyword")
            
            # Check for reasonable ranges
            if params.max_score > 100:
                self.logger.warning("Max score seems unusually high")
            
            if params.population_normalization_factor > 10_000_000:
                self.logger.warning("Population normalization factor seems unusually high")
            
            self.logger.debug("Business parameters validated successfully")
            
        except Exception as e:
            raise ValidationError(f"Business parameters validation failed: {e}")
    
    def validate_cross_references(self, 
                                holiday_periods: Dict[str, HolidayPeriod],
                                regions: Dict[str, RegionData],
                                products: Dict[str, ProductData]) -> None:
        """Validate cross-references between different data objects."""
        try:
            # Check that product seasonal multipliers reference valid holidays
            holiday_names = set(holiday_periods.keys())
            holiday_names.add('normal')  # Allow 'normal' as a default
            
            for product_id, product in products.items():
                for season in product.seasonal_multipliers.keys():
                    if season not in holiday_names:
                        self.logger.warning(
                            f"Product {product_id} references unknown holiday period: {season}"
                        )
            
            # Check that product location suitability matches region types
            region_types = set(region.region_type for region in regions.values())
            
            for product_id, product in products.items():
                for location_type in product.location_suitability.keys():
                    if location_type not in region_types:
                        self.logger.warning(
                            f"Product {product_id} has suitability for unknown region type: {location_type}"
                        )
            
            self.logger.debug("Cross-reference validation completed")
            
        except Exception as e:
            raise ValidationError(f"Cross-reference validation failed: {e}")
    
    def validate_business_logic(self, products: Dict[str, ProductData]) -> None:
        """Validate business logic rules."""
        try:
            for product_id, product in products.items():
                # Check for reasonable profit margins
                profit_margin = product.profit_margin
                if profit_margin < 0.05:  # Less than 5%
                    self.logger.warning(f"Very low profit margin for {product_id}: {profit_margin:.1%}")
                elif profit_margin > 5.0:  # More than 500%
                    self.logger.warning(f"Very high profit margin for {product_id}: {profit_margin:.1%}")
                
                # Check sale time vs perishability
                if (product.perishability_days > 0 and 
                    product.typical_sale_time_days > product.perishability_days):
                    self.logger.warning(
                        f"Product {product_id} sale time ({product.typical_sale_time_days} days) "
                        f"exceeds perishability ({product.perishability_days} days)"
                    )
                
                # Check for digital products with physical storage requirements
                if 'digital' in product.storage_requirements:
                    physical_requirements = [req for req in product.storage_requirements 
                                           if req not in ['digital']]
                    if physical_requirements:
                        self.logger.warning(
                            f"Digital product {product_id} has physical storage requirements: "
                            f"{physical_requirements}"
                        )
            
            self.logger.debug("Business logic validation completed")
            
        except Exception as e:
            raise ValidationError(f"Business logic validation failed: {e}")