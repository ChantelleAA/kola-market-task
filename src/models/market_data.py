"""
Data models for Ghana market inventory recommendation system.

Contains all the data structures used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from decimal import Decimal


@dataclass
class HolidayPeriod:
    """Represents a holiday period that affects market demand."""
    name: str
    months: List[int]
    multiplier: float
    duration_days: int
    description: str = ""
    
    def __post_init__(self):
        """Validate holiday period data."""
        if not 1 <= min(self.months) <= 12 or not 1 <= max(self.months) <= 12:
            raise ValueError(f"Invalid months in holiday period {self.name}")
        if self.multiplier <= 0:
            raise ValueError(f"Multiplier must be positive for {self.name}")
        if self.duration_days <= 0:
            raise ValueError(f"Duration must be positive for {self.name}")


@dataclass
class Infrastructure:
    """Infrastructure metrics for a region."""
    electricity_reliability: float
    cold_storage_access: float
    transport_quality: float
    internet_penetration: float = 0.0
    
    def __post_init__(self):
        """Validate infrastructure metrics."""
        metrics = {
            'electricity_reliability': self.electricity_reliability,
            'cold_storage_access': self.cold_storage_access,
            'transport_quality': self.transport_quality,
            'internet_penetration': self.internet_penetration
        }
        
        for name, value in metrics.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass
class CustomerBehavior:
    """Customer behavior metrics for a region."""
    impulse_buying: float
    brand_consciousness: float
    price_sensitivity: float
    digital_payment_adoption: float = 0.0
    
    def __post_init__(self):
        """Validate customer behavior metrics."""
        metrics = {
            'impulse_buying': self.impulse_buying,
            'brand_consciousness': self.brand_consciousness,
            'price_sensitivity': self.price_sensitivity,
            'digital_payment_adoption': self.digital_payment_adoption
        }
        
        for name, value in metrics.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass
class EconomicIndicators:
    """Economic indicators for a region."""
    average_monthly_income_cedis: float
    unemployment_rate: float
    business_registration_ease: float
    
    def __post_init__(self):
        """Validate economic indicators."""
        if self.average_monthly_income_cedis < 0:
            raise ValueError("Average monthly income cannot be negative")
        if not 0 <= self.unemployment_rate <= 1:
            raise ValueError("Unemployment rate must be between 0 and 1")
        if not 0 <= self.business_registration_ease <= 1:
            raise ValueError("Business registration ease must be between 0 and 1")


@dataclass
class RegionData:
    """Comprehensive data for a geographical region."""
    name: str
    region_type: str
    population: int
    income_level: str
    dominant_work: List[str]
    key_locations: Dict[str, int]
    infrastructure: Dict[str, float]
    customer_behavior: Dict[str, float]
    economic_indicators: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert dictionaries to structured objects."""
        self.infrastructure = Infrastructure(**self.infrastructure)
        self.customer_behavior = CustomerBehavior(**self.customer_behavior)
        if self.economic_indicators:
            self.economic_indicators = EconomicIndicators(**self.economic_indicators)
        
        # Validate basic data
        if self.population <= 0:
            raise ValueError(f"Population must be positive for {self.name}")
        
        valid_income_levels = ['low', 'medium', 'medium-high', 'high']
        if self.income_level not in valid_income_levels:
            raise ValueError(f"Invalid income level for {self.name}")


@dataclass
class SupplierInfo:
    """Supplier information for a product."""
    lead_time_days: int
    minimum_order_quantity: int
    supplier_reliability: float
    
    def __post_init__(self):
        """Validate supplier information."""
        if self.lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")
        if self.minimum_order_quantity <= 0:
            raise ValueError("Minimum order quantity must be positive")
        if not 0 <= self.supplier_reliability <= 1:
            raise ValueError("Supplier reliability must be between 0 and 1")


@dataclass
class ProductData:
    """Comprehensive data for a product."""
    product_id: str
    name: str
    category: str
    cost_price_cedis: float
    selling_price_cedis: float
    perishability_days: int
    typical_sale_time_days: int
    storage_requirements: List[str]
    customer_benefit: str
    risk_factors: List[str]
    seasonal_multipliers: Dict[str, float]
    target_demographics: List[str]
    location_suitability: Dict[str, float]
    supplier_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process and validate product data."""
        # Convert supplier info to structured object
        if self.supplier_info:
            self.supplier_info = SupplierInfo(**self.supplier_info)
        
        # Validate pricing
        if self.cost_price_cedis <= 0:
            raise ValueError(f"Cost price must be positive for {self.product_id}")
        if self.selling_price_cedis <= 0:
            raise ValueError(f"Selling price must be positive for {self.product_id}")
        if self.selling_price_cedis <= self.cost_price_cedis:
            raise ValueError(f"Selling price must be greater than cost price for {self.product_id}")
        
        # Validate time periods
        if self.perishability_days < 0:
            raise ValueError(f"Perishability days cannot be negative for {self.product_id}")
        if self.typical_sale_time_days <= 0:
            raise ValueError(f"Sale time must be positive for {self.product_id}")
        
        # Validate location suitability multipliers
        for location, multiplier in self.location_suitability.items():
            if multiplier <= 0:
                raise ValueError(f"Location suitability must be positive for {self.product_id}")
    
    @property
    def profit_margin(self) -> float:
        """Calculate profit margin as a percentage."""
        return (self.selling_price_cedis - self.cost_price_cedis) / self.cost_price_cedis
    
    @property
    def profit_per_unit(self) -> float:
        """Calculate absolute profit per unit."""
        return self.selling_price_cedis - self.cost_price_cedis
    
    @property
    def sale_velocity_per_month(self) -> float:
        """Calculate how many units can be sold per month."""
        return 30 / self.typical_sale_time_days


@dataclass
class ScoringWeights:
    """Weights for different scoring components."""
    profitability: float
    demand_potential: float
    risk_adjustment: float
    infrastructure_fit: float
    customer_benefit: float
    
    def __post_init__(self):
        """Validate that weights sum to 1.0."""
        total = (self.profitability + self.demand_potential + 
                self.risk_adjustment + self.infrastructure_fit + 
                self.customer_benefit)
        
        if not 0.99 <= total <= 1.01:  # Allow for small floating point errors
            raise ValueError(f"Scoring weights must sum to 1.0, got {total}")
        
        for weight_name, weight_value in self.__dict__.items():
            if not 0 <= weight_value <= 1:
                raise ValueError(f"{weight_name} must be between 0 and 1")


@dataclass
class BusinessParameters:
    """General business parameters for calculations."""
    max_score: float
    population_normalization_factor: int
    location_density_normalization: int
    customer_benefit_keywords: List[str]
    
    def __post_init__(self):
        """Validate business parameters."""
        if self.max_score <= 0:
            raise ValueError("Max score must be positive")
        if self.population_normalization_factor <= 0:
            raise ValueError("Population normalization factor must be positive")
        if self.location_density_normalization <= 0:
            raise ValueError("Location density normalization must be positive")


@dataclass
class FinancialProjection:
    """Financial projections for a product recommendation."""
    cost_price_cedis: float
    selling_price_cedis: float
    profit_margin_percent: str
    estimated_monthly_revenue_cedis: float
    estimated_monthly_profit_cedis: float
    sale_time_days: int
    perishability_days: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'cost_price_cedis': self.cost_price_cedis,
            'selling_price_cedis': self.selling_price_cedis,
            'profit_margin_percent': self.profit_margin_percent,
            'estimated_monthly_revenue_cedis': round(self.estimated_monthly_revenue_cedis, 2),
            'estimated_monthly_profit_cedis': round(self.estimated_monthly_profit_cedis, 2),
            'sale_time_days': self.sale_time_days,
            'perishability_days': self.perishability_days
        }


@dataclass
class BusinessAnalysis:
    """Complete business analysis for a product recommendation."""
    reasoning: str
    detailed_scores: Dict[str, float]
    financial_projection: FinancialProjection
    customer_benefit: str
    risk_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'reasoning': self.reasoning,
            'detailed_scores': self.detailed_scores,
            'financial_projection': self.financial_projection.to_dict(),
            'customer_benefit': self.customer_benefit,
            'risk_factors': self.risk_factors
        }


@dataclass
class ProductRecommendation:
    """A complete product recommendation with analysis."""
    product: str
    category: str
    business_score: float
    analysis: BusinessAnalysis
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'product': self.product,
            'category': self.category,
            'business_score': self.business_score,
            'analysis': self.analysis.to_dict()
        }