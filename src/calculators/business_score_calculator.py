"""
Enhanced Business Score Calculator for Ghana Inventory Recommendation System.

Calculates comprehensive business viability scores with quarterly economic factors,
inflation adjustments, and enhanced demand modeling.
"""

import logging
from typing import Dict, Tuple, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from ..models.market_data import (
    HolidayPeriod, RegionData, ProductData, ScoringWeights, 
    BusinessParameters, BusinessAnalysis, FinancialProjection
)


class BusinessScoreCalculator:
    """Enhanced calculator with quarterly business logic and economic factors."""
    
    def __init__(self,
                 holiday_periods: Dict[str, HolidayPeriod],
                 scoring_weights: ScoringWeights,
                 business_parameters: BusinessParameters, 
                 economic_factors: Dict):
        """
        Initialize the enhanced calculator with economic factors.
        
        Args:
            holiday_periods: Dictionary of holiday periods
            scoring_weights: Weights for different scoring components
            business_parameters: General business parameters
            economic_factors: Economic indicators for quarterly calculations
        """
        self.logger = logging.getLogger(__name__)
        self.holiday_periods = holiday_periods
        self.scoring_weights = scoring_weights
        self.business_parameters = business_parameters
        self.economic_factors = economic_factors

    def calculate_business_score(self,
                               product_data: ProductData,
                               region_data: RegionData,
                               target_month: int) -> Tuple[float, BusinessAnalysis]:
        """
        Calculate comprehensive business viability score with quarterly enhancements.
        
        Args:
            product_data: Product information
            region_data: Region information
            target_month: Target month for analysis (1-12)
        
        Returns:
            Tuple of (business_score, detailed_analysis)
        """
        # Convert month to quarter and calculate adjusted costs
        target_quarter = f"Q{(target_month - 1) // 3 + 1}"
        adjusted_cost_price = self.calculate_inflation_adjusted_cost(product_data, target_quarter)
        
        # Create enhanced product data with adjusted costs
        enhanced_product_data = self._create_enhanced_product_data(
            product_data, adjusted_cost_price, target_quarter
        )
        
        # Initialize scoring components
        scores = {
            'profitability': 0.0,
            'demand_potential': 0.0,
            'risk_adjustment': 0.0,
            'infrastructure_fit': 0.0,
            'customer_benefit': 0.0
        }
        
        reasoning_points = []
        
        # 1. PROFITABILITY SCORE (35% weight) - Enhanced with inflation-adjusted costs
        profitability_score, profit_reasoning = self._calculate_profitability_score(
            enhanced_product_data, region_data
        )
        scores['profitability'] = profitability_score
        reasoning_points.extend(profit_reasoning)
        
        # 2. DEMAND POTENTIAL (30% weight) - Enhanced with quarterly factors
        demand_score, demand_reasoning = self._calculate_enhanced_demand_potential(
            enhanced_product_data, region_data, target_month, target_quarter
        )
        scores['demand_potential'] = demand_score
        reasoning_points.extend(demand_reasoning)
        
        # 3. RISK ADJUSTMENT (20% weight) - Enhanced with economic risks
        risk_score, risk_reasoning = self._calculate_enhanced_risk_adjustment(
            enhanced_product_data, region_data, target_quarter
        )
        scores['risk_adjustment'] = risk_score
        reasoning_points.extend(risk_reasoning)
        
        # 4. INFRASTRUCTURE FIT (10% weight)
        infrastructure_score, infra_reasoning = self._calculate_infrastructure_fit(
            enhanced_product_data, region_data
        )
        scores['infrastructure_fit'] = infrastructure_score
        reasoning_points.extend(infra_reasoning)
        
        # 5. CUSTOMER BENEFIT (5% weight)
        benefit_score, benefit_reasoning = self._calculate_customer_benefit(enhanced_product_data)
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
        
        # Create enhanced financial projections
        financial_projection = self._create_enhanced_financial_projection(
            enhanced_product_data, region_data, target_month, target_quarter, scores['demand_potential']
        )
        
        # Create enhanced business analysis
        analysis = BusinessAnalysis(
            reasoning="; ".join(reasoning_points),
            detailed_scores=scores,
            financial_projection=financial_projection,
            customer_benefit=enhanced_product_data.customer_benefit,
            risk_factors=self._get_enhanced_risk_factors(enhanced_product_data, target_quarter)
        )
        
        return min(final_score, self.business_parameters.max_score), analysis

    def calculate_inflation_adjusted_cost(self, product_data: ProductData, 
                                        target_quarter: str) -> float:
        """Calculate cost price adjusted for inflation and currency fluctuation."""
        # Check if product has the new cost structure
        base_cost_usd = getattr(product_data, 'base_cost_usd', None)
        base_cost_cedis = getattr(product_data, 'base_cost_cedis', None)
        import_dependent = getattr(product_data, 'import_dependent', False)
        
        if import_dependent and base_cost_usd:
            # For imported goods - currency + inflation
            current_rate = self.economic_factors['usd_to_cedis_rate']
            quarter_adjustment = {'Q1': 0.02, 'Q2': -0.01, 'Q3': 0.03, 'Q4': -0.02}
            adjusted_rate = current_rate * (1 + quarter_adjustment.get(target_quarter, 0))
            
            # Apply quarterly inflation
            inflation_rate = self.economic_factors['quarterly_inflation_projection'][target_quarter]
            return base_cost_usd * adjusted_rate * (1 + inflation_rate)
        
        elif base_cost_cedis:
            # For local goods - inflation only (reduced impact)
            inflation_multiplier = 0.7 if not import_dependent else 1.0
            inflation_rate = self.economic_factors['quarterly_inflation_projection'][target_quarter]
            return base_cost_cedis * (1 + inflation_rate * inflation_multiplier)
        
        else:
            # Fallback to existing cost_price_cedis with minimal inflation adjustment
            inflation_rate = self.economic_factors['quarterly_inflation_projection'][target_quarter]
            return product_data.cost_price_cedis * (1 + inflation_rate * 0.5)

    def _create_enhanced_product_data(self, product_data: ProductData, 
                                    adjusted_cost: float, target_quarter: str) -> ProductData:
        """Create enhanced product data with adjusted costs and quarterly factors."""
        # Calculate new metrics based on adjusted costs
        adjusted_profit_per_unit = product_data.selling_price_cedis - adjusted_cost
        adjusted_profit_margin = adjusted_profit_per_unit / adjusted_cost if adjusted_cost > 0 else 0
        
        # Apply quarterly demand multiplier
        quarterly_demand = getattr(product_data, 'quarterly_demand', {})
        quarterly_multiplier = quarterly_demand.get(target_quarter, 1.0)
        adjusted_velocity = product_data.sale_velocity_per_month * quarterly_multiplier
        
        # Create enhanced data - we'll modify the existing object
        # In a production system, you'd want to create a copy
        enhanced_data = product_data
        enhanced_data.cost_price_cedis = adjusted_cost
        enhanced_data.profit_margin = adjusted_profit_margin
        enhanced_data.profit_per_unit = adjusted_profit_per_unit
        enhanced_data.sale_velocity_per_month = adjusted_velocity
        
        return enhanced_data

    def _calculate_profitability_score(self,
                                     product_data: ProductData,
                                     region_data: RegionData) -> Tuple[float, List[str]]:
        """Calculate profitability component score with inflation-adjusted costs."""
        reasoning = []
        
        # Base profit metrics (now using adjusted costs)
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

    def _calculate_enhanced_demand_potential(self,
                                           product_data: ProductData,
                                           region_data: RegionData,
                                           target_month: int,
                                           target_quarter: str) -> Tuple[float, List[str]]:
        """Enhanced demand calculation with quarterly factors."""
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
        
        # Holiday season boost (existing logic)
        holiday_boost = self._get_holiday_boost(product_data, target_month)
        
        # NEW: Quarterly holiday multiplier from monolithic version
        quarterly_holiday_boost = {
            'Q1': 1.4, 'Q2': 1.2, 'Q3': 1.6, 'Q4': 1.8
        }.get(target_quarter, 1.0)
        
        # Enhanced location density factor
        location_density_factor = self._calculate_enhanced_location_density_factor(
            product_data, region_data
        )
        
        # Customer behavior alignment
        behavior_alignment = self._calculate_behavior_alignment(
            product_data, region_data
        )
        
        # NEW: Quarterly demand multiplier
        quarterly_demand = getattr(product_data, 'quarterly_demand', {})
        quarterly_demand_multiplier = quarterly_demand.get(target_quarter, 1.0)
        
        # Enhanced combined demand score
        score = (location_multiplier * population_factor * 
                max(holiday_boost, quarterly_holiday_boost) *
                (1 + location_density_factor) * behavior_alignment * 
                quarterly_demand_multiplier) / 3  # Normalize
        
        # Enhanced reasoning
        if location_multiplier > 1.1:
            reasoning.append(f"Good location fit ({location_multiplier:.1f}x)")
        
        if max(holiday_boost, quarterly_holiday_boost) > 1.3:
            reasoning.append(f"Peak season boost ({max(holiday_boost, quarterly_holiday_boost):.1f}x)")
        
        if quarterly_demand_multiplier > 1.2:
            reasoning.append(f"Peak quarter ({quarterly_demand_multiplier:.1f}x)")
        
        if location_density_factor > 0.5:
            reasoning.append("High venue density")
        
        if population_factor > 1.5:
            reasoning.append("Large population base")
        
        if behavior_alignment > 1.1:
            reasoning.append("Strong customer behavior fit")
        
        return min(score, 10), reasoning

    def _calculate_enhanced_location_density_factor(self,
                                                  product_data: ProductData,
                                                  region_data: RegionData) -> float:
        """Enhanced location density using detailed venue data."""
        relevant_locations = 0
        
        # Enhanced category mapping from monolithic version
        category_location_map = {
            'education': ['schools'],
            'cultural_goods': ['churches', 'mosques'],
            'telecommunications': ['companies', 'estates', 'markets', 'malls'],
            'staple_food': ['companies', 'estates', 'markets'],
            'protein': ['markets', 'companies', 'estates'],
            'basic_home_provisions': ['estates', 'companies', 'markets'],
            'energy_solutions': ['estates', 'companies'],
            'health_products': ['schools', 'companies', 'estates']
        }
        
        relevant_location_types = category_location_map.get(
            product_data.category, ['markets', 'companies']
        )
        
        # Use enhanced key locations if available, fallback to existing
        locations_data = getattr(region_data, 'enhanced_key_locations', region_data.key_locations)
        
        for location_type in relevant_location_types:
            relevant_locations += locations_data.get(location_type, 0)
        
        return min(relevant_locations / self.business_parameters.location_density_normalization, 2.0)

    def _calculate_enhanced_risk_adjustment(self,
                                          product_data: ProductData,
                                          region_data: RegionData,
                                          target_quarter: str) -> Tuple[float, List[str]]:
        """Enhanced risk adjustment with economic and quarterly factors."""
        reasoning = []
        risk_score = 1.0
        
        # Existing perishability risk
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
        
        # NEW: Currency/inflation risk for imported goods
        import_dependent = getattr(product_data, 'import_dependent', False)
        if import_dependent:
            currency_volatility = self.economic_factors.get('currency_volatility', 0.08)
            currency_risk_score = 1.0 - (currency_volatility / 2)
            risk_score *= currency_risk_score
            reasoning.append("Currency risk (imported)")
        
        # Storage infrastructure compatibility
        storage_compatibility = self._assess_storage_compatibility(
            product_data, region_data
        )
        risk_score *= storage_compatibility
        
        if storage_compatibility < 0.8:
            reasoning.append("Storage infrastructure challenges")
        elif storage_compatibility > 1.0:
            reasoning.append("Infrastructure advantage")
        
        # NEW: Quarterly demand risk
        quarterly_demand = getattr(product_data, 'quarterly_demand', {})
        quarterly_multiplier = quarterly_demand.get(target_quarter, 1.0)
        if quarterly_multiplier < 0.8:
            risk_score *= 0.9
            reasoning.append("Low seasonal demand period")
        
        # Existing risk factors assessment
        risk_factor_adjustment = max(0.3, 1.0 - (len(product_data.risk_factors) * 0.1))
        risk_score *= risk_factor_adjustment
        
        if len(product_data.risk_factors) > 3:
            reasoning.append("Multiple risk factors")
        
        return min(risk_score * 10, 10), reasoning

    def _get_enhanced_risk_factors(self, product_data: ProductData, 
                                 target_quarter: str) -> List[str]:
        """Generate enhanced risk factors including economic and quarterly risks."""
        risks = list(product_data.risk_factors)  # Start with existing risks
        
        # Add economic risks
        import_dependent = getattr(product_data, 'import_dependent', False)
        if import_dependent:
            risks.append('Currency exchange rate fluctuation')
            risks.append('Import supply chain disruption')
        
        if product_data.perishability_days < 90:
            risks.append('Short shelf life - spoilage risk')
        
        if product_data.typical_sale_time_days > 30:
            risks.append('Slow inventory turnover')
        
        # Quarterly demand risks
        quarterly_demand = getattr(product_data, 'quarterly_demand', {})
        quarterly_multiplier = quarterly_demand.get(target_quarter, 1.0)
        if quarterly_multiplier < 0.8:
            risks.append('Low seasonal demand period')
        
        # Category-specific quarterly risks
        if product_data.category == 'education' and target_quarter in ['Q2', 'Q4']:
            risks.append('Off-school season demand drop')
        elif product_data.category == 'energy_solutions':
            risks.append('Improving electricity infrastructure threat')
        elif product_data.category == 'cultural_goods':
            risks.append('Fashion and trend changes')
        
        return risks

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
        # This method is kept for backward compatibility
        return self._calculate_enhanced_location_density_factor(product_data, region_data)
    
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
    
    def _create_enhanced_financial_projection(self,
                                            product_data: ProductData,
                                            region_data: RegionData,
                                            target_month: int,
                                            target_quarter: str,
                                            demand_score: float) -> FinancialProjection:
        """Create enhanced financial projections with quarterly factors."""
        # Existing base calculations
        holiday_boost = self._get_holiday_boost(product_data, target_month)
        location_multiplier = product_data.location_suitability.get(
            region_data.region_type, 1.0
        )
        population_factor = min(
            region_data.population / self.business_parameters.population_normalization_factor,
            2.0
        )
        
        # NEW: Quarterly factors
        quarterly_demand = getattr(product_data, 'quarterly_demand', {})
        quarterly_demand_multiplier = quarterly_demand.get(target_quarter, 1.0)
        quarterly_holiday_boost = {
            'Q1': 1.4, 'Q2': 1.2, 'Q3': 1.6, 'Q4': 1.8
        }.get(target_quarter, 1.0)
        
        # Enhanced monthly calculations
        base_monthly_units = product_data.sale_velocity_per_month
        adjusted_units = (base_monthly_units * location_multiplier * 
                         max(holiday_boost, quarterly_holiday_boost) *
                         quarterly_demand_multiplier *
                         min(population_factor, 2.0) * 
                         min(demand_score / 5.0, 2.0))
        
        monthly_revenue = adjusted_units * product_data.selling_price_cedis
        monthly_profit = adjusted_units * product_data.profit_per_unit
        
        return FinancialProjection(
            cost_price_cedis=product_data.cost_price_cedis,  # Now inflation-adjusted
            selling_price_cedis=product_data.selling_price_cedis,
            profit_margin_percent=f"{product_data.profit_margin:.0%}",
            estimated_monthly_revenue_cedis=monthly_revenue,
            estimated_monthly_profit_cedis=monthly_profit,
            sale_time_days=product_data.typical_sale_time_days,
            perishability_days=product_data.perishability_days
        )