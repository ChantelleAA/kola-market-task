"""
Ghana Inventory Recommendation Tool - Enhanced Business Logic
Kola Market Take-Home Challenge

This tool recommends high-demand product categories for Ghanaian locations
based on practical business factors: profitability, risk, customer benefit, and market reality.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse

class GhanaInventoryRecommender:
    def __init__(self):
        """Initialize with Ghana-specific market data and business intelligence."""
        
        # Holiday periods that drive demand spikes
        self.holiday_periods = {
            'christmas_season': {'months': [11, 12], 'multiplier': 1.8, 'duration_days': 60},
            'easter_season': {'months': [3, 4], 'multiplier': 1.4, 'duration_days': 30},
            'independence_day': {'months': [3], 'multiplier': 1.2, 'duration_days': 7},
            'farmers_day': {'months': [12], 'multiplier': 1.3, 'duration_days': 14},
            'back_to_school': {'months': [1, 9], 'multiplier': 1.6, 'duration_days': 21}
        }
        
        # Regional characteristics with business context
        self.regions_data = {
            'Accra': {
                'type': 'urban_coastal',
                'population': 2_400_000,
                'income_level': 'high',
                'dominant_work': ['office_workers', 'traders', 'service_industry'],
                'key_locations': {
                    'churches': 450,
                    'schools': 280,
                    'banks': 95,
                    'companies': 1200,
                    'estates': 85,
                    'markets': 15
                },
                'infrastructure': {
                    'electricity_reliability': 0.85,
                    'cold_storage_access': 0.7,
                    'transport_quality': 0.8
                },
                'customer_behavior': {
                    'impulse_buying': 0.8,
                    'brand_consciousness': 0.9,
                    'price_sensitivity': 0.6
                }
            },
            'Kumasi': {
                'type': 'urban_inland',
                'population': 3_300_000,
                'income_level': 'medium-high',
                'dominant_work': ['farmers', 'traders', 'artisans', 'gold_miners'],
                'key_locations': {
                    'churches': 520,
                    'schools': 340,
                    'banks': 45,
                    'companies': 680,
                    'estates': 35,
                    'markets': 25
                },
                'infrastructure': {
                    'electricity_reliability': 0.75,
                    'cold_storage_access': 0.4,
                    'transport_quality': 0.7
                },
                'customer_behavior': {
                    'impulse_buying': 0.6,
                    'brand_consciousness': 0.6,
                    'price_sensitivity': 0.8
                }
            },
            'Tamale': {
                'type': 'urban_northern',
                'population': 950_000,
                'income_level': 'medium',
                'dominant_work': ['farmers', 'livestock_keepers', 'small_traders'],
                'key_locations': {
                    'churches': 180,
                    'mosques': 120,
                    'schools': 150,
                    'banks': 12,
                    'companies': 200,
                    'estates': 8,
                    'markets': 8
                },
                'infrastructure': {
                    'electricity_reliability': 0.6,
                    'cold_storage_access': 0.2,
                    'transport_quality': 0.5
                },
                'customer_behavior': {
                    'impulse_buying': 0.4,
                    'brand_consciousness': 0.4,
                    'price_sensitivity': 0.9
                }
            },
            'Cape Coast': {
                'type': 'coastal_tourism',
                'population': 230_000,
                'income_level': 'medium',
                'dominant_work': ['fishermen', 'teachers', 'tour_guides', 'students'],
                'key_locations': {
                    'churches': 95,
                    'schools': 45,
                    'banks': 8,
                    'companies': 120,
                    'estates': 12,
                    'markets': 4,
                    'tourist_sites': 8
                },
                'infrastructure': {
                    'electricity_reliability': 0.7,
                    'cold_storage_access': 0.3,
                    'transport_quality': 0.6
                },
                'customer_behavior': {
                    'impulse_buying': 0.5,
                    'brand_consciousness': 0.5,
                    'price_sensitivity': 0.7
                }
            }
        }
        
        # Enhanced product data with business intelligence
        self.products = {
            'rice_imported': {
                'category': 'staple_food',
                'cost_price_cedis': 8.50,
                'selling_price_cedis': 12.00,
                'profit_margin': 0.41,
                'perishability_days': 365,
                'typical_sale_time_days': 14,
                'storage_requirements': 'dry_cool',
                'customer_benefit': 'Essential nutrition, convenient, long-lasting',
                'risk_factors': ['currency_fluctuation', 'import_delays'],
                'seasonal_multiplier': {'christmas_season': 1.4, 'farmers_day': 1.2, 'normal': 1.0},
                'target_demographics': ['families', 'office_workers', 'students'],
                'location_suitability': {
                    'urban_coastal': 1.3,  # Import access
                    'urban_inland': 1.1,
                    'urban_northern': 0.9,
                    'coastal_tourism': 1.0
                }
            },
            'sardines_canned': {
                'category': 'protein',
                'cost_price_cedis': 6.00,
                'selling_price_cedis': 8.50,
                'profit_margin': 0.42,
                'perishability_days': 730,
                'typical_sale_time_days': 21,
                'storage_requirements': 'room_temperature',
                'customer_benefit': 'Affordable protein, long shelf life, ready-to-eat',
                'risk_factors': ['competition_from_fresh_fish'],
                'seasonal_multiplier': {'christmas_season': 1.6, 'easter_season': 1.3, 'normal': 1.0},
                'target_demographics': ['low_income_families', 'students', 'workers'],
                'location_suitability': {
                    'urban_coastal': 1.1,
                    'urban_inland': 1.3,  # Less fresh fish competition
                    'urban_northern': 1.2,
                    'coastal_tourism': 0.8  # Fresh fish preferred
                }
            },
            'mobile_phone_credit': {
                'category': 'telecommunications',
                'cost_price_cedis': 95.00,  # GHS 100 credit costs GHS 95
                'selling_price_cedis': 100.00,
                'profit_margin': 0.05,
                'perishability_days': 0,  # Non-perishable
                'typical_sale_time_days': 1,  # Very fast turnover
                'storage_requirements': 'digital',
                'customer_benefit': 'Essential communication, instant delivery, universal need',
                'risk_factors': ['network_technical_issues'],
                'seasonal_multiplier': {'christmas_season': 1.3, 'back_to_school': 1.2, 'normal': 1.0},
                'target_demographics': ['everyone_with_phone'],
                'location_suitability': {
                    'urban_coastal': 1.2,
                    'urban_inland': 1.1,
                    'urban_northern': 1.0,
                    'coastal_tourism': 1.1
                }
            },
            'solar_lanterns': {
                'category': 'energy_solutions',
                'cost_price_cedis': 45.00,
                'selling_price_cedis': 75.00,
                'profit_margin': 0.67,
                'perishability_days': 0,
                'typical_sale_time_days': 45,
                'storage_requirements': 'dry',
                'customer_benefit': 'Reliable lighting, no electricity bills, durable',
                'risk_factors': ['improving_electricity_grid', 'product_defects'],
                'seasonal_multiplier': {'christmas_season': 1.2, 'normal': 1.0},
                'target_demographics': ['rural_families', 'students', 'small_businesses'],
                'location_suitability': {
                    'urban_coastal': 0.6,  # Good electricity
                    'urban_inland': 0.8,
                    'urban_northern': 1.4,  # Poor electricity
                    'coastal_tourism': 0.9
                }
            },
            'kente_accessories': {
                'category': 'cultural_goods',
                'cost_price_cedis': 25.00,
                'selling_price_cedis': 60.00,
                'profit_margin': 1.4,
                'perishability_days': 0,
                'typical_sale_time_days': 60,
                'storage_requirements': 'dry_protected',
                'customer_benefit': 'Cultural identity, special occasions, gifts, tourism appeal',
                'risk_factors': ['seasonal_demand', 'fashion_changes'],
                'seasonal_multiplier': {'christmas_season': 2.1, 'independence_day': 1.8, 'normal': 0.6},
                'target_demographics': ['cultural_events', 'tourists', 'gift_buyers'],
                'location_suitability': {
                    'urban_coastal': 1.1,  # Tourists
                    'urban_inland': 1.5,   # Cultural center
                    'urban_northern': 0.8,
                    'coastal_tourism': 1.3  # Tourist demand
                }
            },
            'school_supplies_basic': {
                'category': 'education',
                'cost_price_cedis': 15.00,
                'selling_price_cedis': 25.00,
                'profit_margin': 0.67,
                'perishability_days': 0,
                'typical_sale_time_days': 30,
                'storage_requirements': 'dry',
                'customer_benefit': 'Educational advancement, required for school, affordable',
                'risk_factors': ['academic_calendar_changes'],
                'seasonal_multiplier': {'back_to_school': 2.5, 'normal': 0.4},
                'target_demographics': ['parents', 'students', 'teachers'],
                'location_suitability': {
                    'urban_coastal': 1.2,
                    'urban_inland': 1.1,
                    'urban_northern': 1.0,
                    'coastal_tourism': 1.3  # University town
                }
            },
            'mosquito_nets_treated': {
                'category': 'health_products',
                'cost_price_cedis': 18.00,
                'selling_price_cedis': 35.00,
                'profit_margin': 0.94,
                'perishability_days': 1095,  # 3 years effectiveness
                'typical_sale_time_days': 25,
                'storage_requirements': 'dry_packaged',
                'customer_benefit': 'Malaria prevention, better sleep, family health',
                'risk_factors': ['government_free_distribution', 'seasonal_awareness'],
                'seasonal_multiplier': {'normal': 1.0},  # Steady year-round need
                'target_demographics': ['families_with_children', 'health_conscious'],
                'location_suitability': {
                    'urban_coastal': 0.9,
                    'urban_inland': 1.1,
                    'urban_northern': 1.3,  # Higher malaria risk
                    'coastal_tourism': 0.8
                }
            },
            'palm_oil_local': {
                'category': 'cooking_essentials',
                'cost_price_cedis': 28.00,
                'selling_price_cedis': 35.00,
                'profit_margin': 0.25,
                'perishability_days': 180,
                'typical_sale_time_days': 10,
                'storage_requirements': 'cool_sealed',
                'customer_benefit': 'Traditional cooking, authentic taste, supports local farmers',
                'risk_factors': ['price_volatility', 'quality_variations', 'spoilage'],
                'seasonal_multiplier': {'christmas_season': 1.4, 'easter_season': 1.2, 'normal': 1.0},
                'target_demographics': ['traditional_cooks', 'families', 'restaurants'],
                'location_suitability': {
                    'urban_coastal': 1.0,
                    'urban_inland': 1.3,  # Production area
                    'urban_northern': 1.1,
                    'coastal_tourism': 0.9
                }
            }
        }
    
    def calculate_business_score(self, product: str, location: str, target_month: int = None) -> Tuple[float, Dict]:
        """Calculate comprehensive business viability score."""
        if location not in self.regions_data or product not in self.products:
            return 0.0, {"error": "Invalid location or product"}
        
        region_data = self.regions_data[location]
        product_data = self.products[product]
        target_month = target_month or datetime.now().month
        
        # Initialize scoring components
        scores = {
            'profitability': 0,
            'demand_potential': 0,
            'risk_adjustment': 0,
            'infrastructure_fit': 0,
            'customer_benefit': 0
        }
        
        reasoning = []
        
        # 1. PROFITABILITY SCORE (35% weight)
        profit_margin = product_data['profit_margin']
        sale_velocity = 30 / product_data['typical_sale_time_days']  # Sales per month
        monthly_profit_potential = profit_margin * sale_velocity
        
        scores['profitability'] = min(monthly_profit_potential * 10, 10)  # Cap at 10
        if profit_margin > 0.5:
            reasoning.append(f"High profit margin ({profit_margin:.0%})")
        if sale_velocity > 1:
            reasoning.append(f"Fast turnover ({product_data['typical_sale_time_days']} days)")
        
        # 2. DEMAND POTENTIAL (30% weight)
        # Population and location suitability
        location_multiplier = product_data['location_suitability'].get(region_data['type'], 1.0)
        population_factor = min(region_data['population'] / 500_000, 3.0)
        
        # Holiday season boost
        holiday_boost = 1.0
        for holiday, data in self.holiday_periods.items():
            if target_month in data['months'] and holiday in product_data['seasonal_multiplier']:
                holiday_boost = max(holiday_boost, product_data['seasonal_multiplier'][holiday])
        
        # Key locations that drive demand
        relevant_locations = 0
        if product_data['category'] in ['education']:
            relevant_locations = region_data['key_locations'].get('schools', 0)
        elif product_data['category'] in ['cultural_goods']:
            relevant_locations = region_data['key_locations'].get('churches', 0)
        elif product_data['category'] in ['telecommunications', 'staple_food']:
            relevant_locations = region_data['key_locations'].get('companies', 0) + region_data['key_locations'].get('estates', 0)
        
        location_density_factor = min(relevant_locations / 100, 2.0)
        
        scores['demand_potential'] = location_multiplier * population_factor * holiday_boost * (1 + location_density_factor)
        
        if location_multiplier > 1.1:
            reasoning.append(f"Good location fit ({location_multiplier:.1f}x)")
        if holiday_boost > 1.2:
            reasoning.append(f"Holiday season boost ({holiday_boost:.1f}x)")
        if location_density_factor > 0.5:
            reasoning.append(f"High venue density")
        
        # 3. RISK ADJUSTMENT (20% weight)
        # Perishability risk
        if product_data['perishability_days'] > 365:
            perishability_score = 1.0
        elif product_data['perishability_days'] > 180:
            perishability_score = 0.8
        elif product_data['perishability_days'] > 30:
            perishability_score = 0.6
        else:
            perishability_score = 0.3
        
        # Infrastructure compatibility
        infrastructure_score = 1.0
        storage_req = product_data['storage_requirements']
        if 'cold' in storage_req:
            infrastructure_score *= region_data['infrastructure']['cold_storage_access']
        if 'electricity' in storage_req or product_data['category'] == 'energy_solutions':
            # Energy products benefit from poor electricity
            if product_data['category'] == 'energy_solutions':
                infrastructure_score *= (1.2 - region_data['infrastructure']['electricity_reliability'])
            else:
                infrastructure_score *= region_data['infrastructure']['electricity_reliability']
        
        scores['risk_adjustment'] = perishability_score * infrastructure_score
        
        if perishability_score < 0.7:
            reasoning.append("Perishability risk")
        if infrastructure_score > 1.0:
            reasoning.append("Infrastructure advantage")
        elif infrastructure_score < 0.8:
            reasoning.append("Infrastructure challenges")
        
        # 4. INFRASTRUCTURE FIT (10% weight)
        scores['infrastructure_fit'] = infrastructure_score
        
        # 5. CUSTOMER BENEFIT (5% weight)
        benefit_keywords = ['essential', 'affordable', 'convenient', 'durable', 'health']
        benefit_score = sum(1 for keyword in benefit_keywords 
                          if keyword in product_data['customer_benefit'].lower()) / len(benefit_keywords)
        scores['customer_benefit'] = benefit_score
        
        # Calculate final weighted score
        weights = {
            'profitability': 0.35,
            'demand_potential': 0.30,
            'risk_adjustment': 0.20,
            'infrastructure_fit': 0.10,
            'customer_benefit': 0.05
        }
        
        final_score = sum(scores[component] * weights[component] for component in scores)
        
        # Add financial projections
        monthly_revenue_potential = (product_data['selling_price_cedis'] * sale_velocity * 
                                   location_multiplier * holiday_boost * min(population_factor, 2.0))
        monthly_profit_potential = monthly_revenue_potential * (profit_margin / (1 + profit_margin))
        
        return final_score, {
            'reasoning': "; ".join(reasoning),
            'detailed_scores': scores,
            'financial_projection': {
                'cost_price_cedis': product_data['cost_price_cedis'],
                'selling_price_cedis': product_data['selling_price_cedis'],
                'profit_margin_percent': f"{profit_margin:.0%}",
                'estimated_monthly_revenue_cedis': round(monthly_revenue_potential, 2),
                'estimated_monthly_profit_cedis': round(monthly_profit_potential, 2),
                'sale_time_days': product_data['typical_sale_time_days'],
                'perishability_days': product_data['perishability_days']
            },
            'customer_benefit': product_data['customer_benefit'],
            'risk_factors': product_data['risk_factors']
        }
    
    def get_recommendations(self, location: str, num_recommendations: int = 5, target_month: int = None) -> List[Dict]:
        """Get top business-viable product recommendations for a location."""
        if location not in self.regions_data:
            return []
        
        target_month = target_month or datetime.now().month
        recommendations = []
        
        for product, product_data in self.products.items():
            score, analysis = self.calculate_business_score(product, location, target_month)
            
            recommendations.append({
                'product': product.replace('_', ' ').title(),
                'category': product_data['category'].replace('_', ' ').title(),
                'business_score': round(score, 2),
                'analysis': analysis
            })
        
        # Sort by business score and return top N
        recommendations.sort(key=lambda x: x['business_score'], reverse=True)
        return recommendations[:num_recommendations]
    
    def print_business_recommendations(self, location: str, target_month: int = None):
        """Print formatted business recommendations for a location."""
        recommendations = self.get_recommendations(location, 5, target_month)
        target_month = target_month or datetime.now().month
        month_name = datetime(2024, target_month, 1).strftime('%B')
        
        region_info = self.regions_data[location]
        
        print(f"\n{'='*80}")
        print(f"🏪 BUSINESS INVENTORY RECOMMENDATIONS FOR {location.upper()}")
        print(f"📅 Target Month: {month_name}")
        print(f"👥 Population: {region_info['population']:,} | Work: {', '.join(region_info['dominant_work'])}")
        print(f"🏢 Key Venues: {region_info['key_locations']['churches']} churches, {region_info['key_locations']['schools']} schools, {region_info['key_locations']['companies']} companies")
        print(f"{'='*80}")
        
        for i, rec in enumerate(recommendations, 1):
            analysis = rec['analysis']
            financial = analysis['financial_projection']
            
            print(f"\n{i}. 📦 {rec['product']} ({rec['category']})")
            print(f"   ⭐ Business Score: {rec['business_score']}/10")
            print(f"   💰 Cost: ¢{financial['cost_price_cedis']} → Sell: ¢{financial['selling_price_cedis']} (Margin: {financial['profit_margin_percent']})")
            print(f"   📈 Monthly Potential: ¢{financial['estimated_monthly_profit_cedis']} profit | ¢{financial['estimated_monthly_revenue_cedis']} revenue")
            print(f"   ⏱️  Sale Time: {financial['sale_time_days']} days | Shelf Life: {financial['perishability_days']} days")
            print(f"   ✅ Customer Benefit: {analysis['customer_benefit']}")
            print(f"   📊 Analysis: {analysis['reasoning']}")
            if analysis['risk_factors']:
                print(f"   ⚠️  Risks: {', '.join(analysis['risk_factors'])}")

def main():
    """Command line interface for the business-focused inventory recommender."""
    parser = argparse.ArgumentParser(description='Ghana Business Inventory Recommendation Tool')
    parser.add_argument('--locations', nargs='+', 
                       choices=['Accra', 'Kumasi', 'Tamale', 'Cape Coast'],
                       default=['Accra', 'Kumasi'],
                       help='Locations to analyze (default: Accra Kumasi)')
    parser.add_argument('--month', type=int, choices=range(1, 13),
                       help='Target month (1-12, default: current month)')
    
    args = parser.parse_args()
    
    recommender = GhanaInventoryRecommender()
    
    for location in args.locations:
        recommender.print_business_recommendations(location, args.month)

if __name__ == "__main__":
    # Demo for business presentation
    recommender = GhanaInventoryRecommender()
    
    print("🇬🇭 GHANA BUSINESS INVENTORY RECOMMENDATION TOOL")
    print("Kola Market Take-Home Challenge - Enhanced Business Logic")
    print("Focus: Profitability, Customer Benefit, Risk Management")
    print("="*80)
    
    # Demo for December (Christmas season)
    locations = ['Accra', 'Kumasi']
    
    for location in locations:
        recommender.print_business_recommendations(location, 12)  # December