"""
Business Score Calculator for Ghana Inventory Recommendation System.

Calculates comprehensive business viability scores based on multiple factors.
"""

import logging
from typing import Dict, Tuple, List
from datetime import datetime

from ..models.market_data import (
    HolidayPeriod, RegionData, ProductData, ScoringWeights, 
    BusinessParameters, BusinessAnalysis, FinancialProjection
)


class BusinessScoreCalculator:
    """Calculates business viability scores for product-location combinations."""
    
    def __init__(self,
                 holiday_periods: Dict[str, HolidayPeriod],
                 scoring_weights: ScoringWeights,
                 business_parameters: BusinessParameters):
        """
        Initialize the calculator with configuration data.
        
        Args:
            holiday_periods: Dictionary of holiday periods
            scoring_weights: Weights for different scoring components
            business_parameters: General business parameters
        """
        self.logger = logging.getLogger(__name__)
        self.holiday_periods = holiday_periods
        self.scoring_weights = scoring_weights
        self.business_parameters = business_parameters
    
    def calculate_business_score(self,
                               product_data: ProductData,
                               region_data: RegionData,
                               target_month: int) -> Tuple[float, BusinessAnalysis]:
        """
        Calculate comprehensive business viability score.
        
        Args:
            product_data: Product information
            region_data: Region information
            target_month: Target month for analysis (1-12)
        
        Returns:
            Tuple of (business_score, detailed_analysis)
        """
        # Initialize scoring components
        scores = {
            'profitability': 0.0,
            'demand_potential': 0.0,
            'risk_adjustment': 0.0,
            'infrastructure_fit': 0.0,
            'customer_benefit': 0.0
        }
        
        reasoning_points = []
        
        # 1. PROFITABILITY SCORE (35% weight)
        profitability_score, profit_reasoning = self._calculate_profitability_score(
            product_data, region_data
        )
        scores['profitability'] = profitability_score
        reasoning_points.extend(profit_reasoning)
        
        # 2. DEMAND POTENTIAL (30% weight)
        demand_score, demand_reasoning = self._calculate_demand_potential(
            product_data, region_data, target_month
        )
        scores['demand_potential'] = demand_score
        reasoning_points.extend(demand_reasoning)
        
        # 3. RISK ADJUSTMENT (20% weight)
        risk_score, risk_reasoning = self._calculate_risk_adjustment(
            product_data, region_data
        )
        scores['risk_adjustment'] = risk_score
        reasoning_points.extend(risk_reasoning)
        
        # 4. INFRASTRUCTURE FIT (10% weight)
        infrastructure_score, infra_reasoning = self._calculate_infrastructure_fit(
            product_data, region_data
        )
        scores['infrastructure_fit'] = infrastructure_score
        reasoning_points.extend(infra_reasoning)
        
        # 5. CUSTOMER BENEFIT (5% weight)
        benefit_score, benefit_reasoning = self._calculate_customer_benefit(product_data)
        scores['customer_benefit'] = benefit_score
        reasoning_points.extend(benefit_reasoning)
        
        # Calculate weighted final score
        final_score = (
            scores['profitability'] * self.scoring_weights.profitability +
            scores['demand_potential'] * self.scoring_weights.demand_potential +
            scores['risk_adjustment'] * self.scoring_weights.risk_adjustment +
            scores['infrastructure_fit'] * self.scoring_weights.infrastructure_fit +
            scores['customer_benefit'] * self.scoring_weights.customer_benefit
        )
        
        # Create financial projections
        financial_projection = self._create_financial_projection(
            product_data, region_data, target_month, scores['demand_potential']
        )
        
        # Create business analysis
        analysis = BusinessAnalysis(
            reasoning="; ".join(reasoning_points),
            detailed_scores=scores,
            financial_projection=financial_projection,
            customer_benefit=product_data.customer_benefit,
            risk_factors=product_data.risk_factors
        )
        
        return min(final_score, self.business_parameters.max_score), analysis
    
    def _calculate_profitability_score(self,
                                     product_data: ProductData,
                                     region_data: RegionData) -> Tuple[float, List[str]]:
        """Calculate profitability component score."""
        reasoning = []
        
        # Base profit metrics
        profit_margin = product_data.profit_margin
        sale_velocity = product_data.sale_velocity_per_month
        monthly_profit_potential = profit_margin * sale_velocity
        
        # Score based on profit potential (scaled to max 10)
        score = min(monthly_profit_potential * 10, 10)
        
        # Add reasoning
        if profit_margin > 0.5:
            reasoning.append(f"High profit margin ({profit_margin:.0%})")
        elif profit_margin > 0.3:
            reasoning.append(f"Good profit margin ({profit_margin:.0%})")
        
        if sale_velocity > 1:
            reasoning.append(f"Fast turnover ({product_data.typical_sale_time_days} days)")
        
        # Adjust for income level compatibility
        income_adjustment = self._get_income_level_adjustment(
            product_data, region_data.income_level
        )
        score *= income_adjustment
        
        if income_adjustment != 1.0:
            reasoning.append(f"Income level adjustment ({income_adjustment:.1f}x)")
        
        return score, reasoning
    
    def _calculate_demand_potential(self,
                                  product_data: ProductData,
                                  region_data: RegionData,
                                  target_month: int) -> Tuple[float, List[str]]:
        """Calculate demand potential component score."""
        reasoning = []
        
        # Base location suitability
        location_multiplier = product_data.location_suitability.get(
            region_data.region_type, 1.0
        )
        
        # Population factor (normalized)
        population_factor = min(
            region_data.population / self.business_parameters.population_normalization_factor,
            3.0
        )
        
        # Holiday season boost
        holiday_boost = self._get_holiday_boost(product_data, target_month)
        
        # Key locations that drive demand
        location_density_factor = self._calculate_location_density_factor(
            product_data, region_data
        )
        
        # Customer behavior alignment
        behavior_alignment = self._calculate_behavior_alignment(
            product_data, region_data
        )
        
        # Combined demand score
        score = (location_multiplier * population_factor * holiday_boost * 
                (1 + location_density_factor) * behavior_alignment)
        
        # Add reasoning
        if location_multiplier > 1.1:
            reasoning.append(f"Good location fit ({location_multiplier:.1f}x)")
        
        if holiday_boost > 1.2:
            reasoning.append(f"Holiday season boost ({holiday_boost:.1f}x)")
        
        if location_density_factor > 0.5:
            reasoning.append("High venue density")
        
        if population_factor > 1.5:
            reasoning.append("Large population base")
        
        if behavior_alignment > 1.1:
            reasoning.append("Strong customer behavior fit")
        
        return min(score, 10), reasoning
    
    def _calculate_risk_adjustment(self,
                                 product_data: ProductData,
                                 region_data: RegionData) -> Tuple[float, List[str]]:
        """Calculate risk adjustment component score."""
        reasoning = []
        risk_score = 1.0
        
        # Perishability risk
        if product_data.perishability_days == 0:
            perishability_score = 1.0
        elif product_data.perishability_days > 365:
            perishability_score = 1.0
        elif product_data.perishability_days > 180:
            perishability_score = 0.8
        elif product_data.perishability_days > 30:
            perishability_score = 0.6
        else:
            perishability_score = 0.3
            reasoning.append("High perishability risk")
        
        risk_score *= perishability_score
        
        # Storage infrastructure compatibility
        storage_compatibility = self._assess_storage_compatibility(
            product_data, region_data
        )
        risk_score *= storage_compatibility
        
        if storage_compatibility < 0.8:
            reasoning.append("Storage infrastructure challenges")
        elif storage_compatibility > 1.0:
            reasoning.append("Infrastructure advantage")
        
        # Risk factors assessment
        risk_factor_adjustment = max(0.3, 1.0 - (len(product_data.risk_factors) * 0.1))
        risk_score *= risk_factor_adjustment
        
        if len(product_data.risk_factors) > 3:
            reasoning.append("Multiple risk factors")
        
        return min(risk_score * 10, 10), reasoning
    
    def _calculate_infrastructure_fit(self,
                                    product_data: ProductData,
                                    region_data: RegionData) -> Tuple[float, List[str]]:
        """Calculate infrastructure fit component score."""
        reasoning = []
        
        compatibility_score = self._assess_storage_compatibility(
            product_data, region_data
        )
        
        # Special handling for energy products (benefit from poor electricity)
        if product_data.category == 'energy_solutions':
            electricity_factor = 1.2 - region_data.infrastructure.electricity_reliability
            compatibility_score *= electricity_factor
            if electricity_factor > 1.0:
                reasoning.append("Benefits from electricity challenges")
        
        # Transport quality affects all physical products
        if 'digital' not in product_data.storage_requirements:
            transport_factor = 0.5 + (region_data.infrastructure.transport_quality * 0.5)
            compatibility_score *= transport_factor
            
            if region_data.infrastructure.transport_quality < 0.6:
                reasoning.append("Transport quality concerns")
        
        score = compatibility_score * 10
        return min(score, 10), reasoning
    
    def _calculate_customer_benefit(self, product_data: ProductData) -> Tuple[float, List[str]]:
        """Calculate customer benefit component score."""
        reasoning = []
        
        # Count benefit keywords in description
        benefit_keywords = self.business_parameters.customer_benefit_keywords
        benefit_text = product_data.customer_benefit.lower()
        
        keyword_count = sum(
            1 for keyword in benefit_keywords
            if keyword in benefit_text
        )
        
        score = (keyword_count / len(benefit_keywords)) * 10
        
        if keyword_count >= 3:
            reasoning.append("Strong customer benefits")
        elif keyword_count >= 2:
            reasoning.append("Good customer benefits")
        
        return score, reasoning
    
    def _get_holiday_boost(self, product_data: ProductData, target_month: int) -> float:
        """Calculate holiday boost multiplier for target month."""
        boost = 1.0
        
        for holiday_name, holiday_data in self.holiday_periods.items():
            if (target_month in holiday_data.months and 
                holiday_name in product_data.seasonal_multipliers):
                boost = max(boost, product_data.seasonal_multipliers[holiday_name])
        
        return boost
    
    def _calculate_location_density_factor(self,
                                         product_data: ProductData,
                                         region_data: RegionData) -> float:
        """Calculate factor based on relevant location density."""
        relevant_locations = 0
        
        # Map product categories to relevant locations
        category_location_map = {
            'education': ['schools'],
            'cultural_goods': ['churches', 'mosques'],
            'telecommunications': ['companies', 'estates', 'markets'],
            'staple_food': ['companies', 'estates', 'markets'],
            'health_products': ['schools', 'companies', 'estates']
        }
        
        relevant_location_types = category_location_map.get(
            product_data.category, ['markets', 'companies']
        )
        
        for location_type in relevant_location_types:
            relevant_locations += region_data.key_locations.get(location_type, 0)
        
        return min(relevant_locations / self.business_parameters.location_density_normalization, 2.0)
    
    def _calculate_behavior_alignment(self,
                                    product_data: ProductData,
                                    region_data: RegionData) -> float:
        """Calculate alignment with customer behavior patterns."""
        alignment = 1.0
        
        # High-margin luxury items need low price sensitivity
        if product_data.profit_margin > 1.0:  # >100% margin
            alignment *= (1.2 - region_data.customer_behavior.price_sensitivity)
        
        # Impulse buying affects certain categories
        impulse_categories = ['telecommunications', 'cultural_goods']
        if product_data.category in impulse_categories:
            alignment *= (0.8 + region_data.customer_behavior.impulse_buying * 0.4)
        
        # Brand consciousness affects premium products
        if product_data.selling_price_cedis > 50:
            alignment *= (0.7 + region_data.customer_behavior.brand_consciousness * 0.6)
        
        return alignment
    
    def _get_income_level_adjustment(self, product_data: ProductData, income_level: str) -> float:
        """Get adjustment factor based on income level compatibility."""
        price_brackets = {
            'low': (0, 25),
            'medium': (15, 75),
            'medium-high': (40, 150),
            'high': (75, 500)
        }
        
        suitable_range = price_brackets.get(income_level, (0, 1000))
        price = product_data.selling_price_cedis
        
        if suitable_range[0] <= price <= suitable_range[1]:
            return 1.0
        elif price < suitable_range[0]:
            return 0.8  # Might be seen as cheap/low quality
        else:
            return max(0.3, 1.0 - ((price - suitable_range[1]) / suitable_range[1]))
    
    def _assess_storage_compatibility(self,
                                    product_data: ProductData,
                                    region_data: RegionData) -> float:
        """Assess compatibility between storage requirements and infrastructure."""
        compatibility = 1.0
        
        requirements = product_data.storage_requirements
        
        if 'cold' in requirements or 'cool' in requirements:
            compatibility *= region_data.infrastructure.cold_storage_access
        
        if 'digital' in requirements:
            # Digital products need good infrastructure
            compatibility *= region_data.infrastructure.electricity_reliability
        
        # Dry storage is generally available but quality varies
        if 'dry' in requirements:
            compatibility *= min(1.0, 0.7 + region_data.infrastructure.transport_quality * 0.3)
        
        return compatibility
    
    def _create_financial_projection(self,
                                   product_data: ProductData,
                                   region_data: RegionData,
                                   target_month: int,
                                   demand_score: float) -> FinancialProjection:
        """Create financial projections based on analysis."""
        # Base calculations
        holiday_boost = self._get_holiday_boost(product_data, target_month)
        location_multiplier = product_data.location_suitability.get(
            region_data.region_type, 1.0
        )
        population_factor = min(
            region_data.population / self.business_parameters.population_normalization_factor,
            2.0
        )
        
        # Monthly revenue potential
        base_monthly_units = product_data.sale_velocity_per_month
        adjusted_units = (base_monthly_units * location_multiplier * 
                         holiday_boost * min(population_factor, 2.0) * 
                         min(demand_score / 5.0, 2.0))
        
        monthly_revenue = adjusted_units * product_data.selling_price_cedis
        monthly_profit = adjusted_units * product_data.profit_per_unit
        
        return FinancialProjection(
            cost_price_cedis=product_data.cost_price_cedis,
            selling_price_cedis=product_data.selling_price_cedis,
            profit_margin_percent=f"{product_data.profit_margin:.0%}",
            estimated_monthly_revenue_cedis=monthly_revenue,
            estimated_monthly_profit_cedis=monthly_profit,
            sale_time_days=product_data.typical_sale_time_days,
            perishability_days=product_data.perishability_days
        )