"""
Enhanced Ghana Inventory Recommendation System - Main Recommender Class

Provides quarterly business intelligence and enhanced inventory recommendations.
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from .config_manager import ConfigManager
from .models.market_data import (
    ProductRecommendation, BusinessAnalysis, FinancialProjection,
    RegionData, ProductData, EconomicFactors, QuarterData
)
from .calculators.business_score_calculator import BusinessScoreCalculator
from .utils.formatters import RecommendationFormatter


class GhanaInventoryRecommender:
    """
    Enhanced main class for generating inventory recommendations with quarterly intelligence.
    
    Provides comprehensive business analysis including quarterly seasonal patterns,
    economic factors, inflation adjustments, and enhanced demand modeling.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the enhanced recommender with configuration data.
        
        Args:
            config_manager: Configured instance of ConfigManager
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # Initialize enhanced business score calculator with economic factors
        self.score_calculator = BusinessScoreCalculator(
            config_manager.get_enhanced_holiday_periods(),
            config_manager.get_scoring_weights(),
            config_manager.get_business_parameters(),
            config_manager.get_economic_factors()
        )
        
        # Initialize formatter
        self.formatter = RecommendationFormatter()
        
        self.logger.info("Enhanced Ghana Inventory Recommender initialized successfully")
    
    def get_recommendations(self,
                          location: str,
                          num_recommendations: int = 5,
                          target_month: Optional[int] = None) -> List[ProductRecommendation]:
        """
        Get top business-viable product recommendations for a location.
        
        Args:
            location: Name of the location to analyze
            num_recommendations: Number of recommendations to return
            target_month: Target month (1-12), defaults to current month
        
        Returns:
            List of product recommendations sorted by business score
        
        Raises:
            ValueError: If location is not found or invalid parameters
        """
        # Validate inputs
        region_data = self.config_manager.get_region(location)
        if not region_data:
            available_regions = list(self.config_manager.get_regions().keys())
            raise ValueError(f"Location '{location}' not found. Available: {available_regions}")
        
        if num_recommendations <= 0:
            raise ValueError("Number of recommendations must be positive")
        
        target_month = target_month or datetime.now().month
        if not 1 <= target_month <= 12:
            raise ValueError("Target month must be between 1 and 12")
        
        self.logger.info(f"Generating {num_recommendations} recommendations for {location}, month {target_month}")
        
        # Get all products and calculate scores
        products = self.config_manager.get_products()
        recommendations = []
        
        for product_id, product_data in products.items():
            try:
                score, analysis = self.score_calculator.calculate_business_score(
                    product_data=product_data,
                    region_data=region_data,
                    target_month=target_month
                )
                
                recommendation = ProductRecommendation(
                    product=product_data.name,
                    category=product_data.category.replace('_', ' ').title(),
                    business_score=round(score, 2),
                    analysis=analysis
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                self.logger.warning(f"Error calculating score for {product_id}: {e}")
                continue
        
        # Sort by business score and return top N
        recommendations.sort(key=lambda x: x.business_score, reverse=True)
        top_recommendations = recommendations[:num_recommendations]
        
        self.logger.info(f"Generated {len(top_recommendations)} recommendations for {location}")
        return top_recommendations
    
    def get_quarterly_recommendations(self, 
                                    location: str, 
                                    target_quarter: str = None,
                                    num_recommendations: int = 15) -> List[ProductRecommendation]:
        """
        Get recommendations optimized for a specific quarter with seasonal intelligence.
        
        Args:
            location: Name of the location to analyze
            target_quarter: Target quarter (Q1-Q4), defaults to current quarter
            num_recommendations: Number of recommendations to return
        
        Returns:
            List of product recommendations optimized for the quarter
        """
        target_quarter = target_quarter or self.config_manager.get_current_quarter()
        
        # Convert quarter to representative month for analysis
        quarter_to_month = {'Q1': 2, 'Q2': 5, 'Q3': 8, 'Q4': 11}
        target_month = quarter_to_month.get(target_quarter, datetime.now().month)
        
        self.logger.info(f"Generating quarterly recommendations for {location}, {target_quarter}")
        
        recommendations = self.get_recommendations(location, num_recommendations * 2, target_month)
        
        # Filter and enhance for quarterly performance
        quarterly_enhanced = []
        for rec in recommendations:
            # Get the original product data to check quarterly performance
            product_data = None
            for pid, pdata in self.config_manager.get_products().items():
                if pdata.name == rec.product:
                    product_data = pdata
                    break
            
            if product_data:
                quarterly_multiplier = product_data.quarterly_demand.get(target_quarter, 1.0)
                # Boost score for products that perform well in this quarter
                if quarterly_multiplier > 1.1:
                    rec.business_score *= 1.1  # Slight boost for quarterly performers
                quarterly_enhanced.append(rec)
        
        # Re-sort and return top recommendations
        quarterly_enhanced.sort(key=lambda x: x.business_score, reverse=True)
        return quarterly_enhanced[:num_recommendations]
    
    def print_quarterly_recommendations(self, 
                                      location: str, 
                                      target_quarter: str = None,
                                      sort_by: str = 'business_score') -> None:
        """
        Print quarterly recommendations with enhanced formatting like the monolithic version.
        
        Args:
            location: Name of the location to analyze
            target_quarter: Target quarter (Q1-Q4), defaults to current quarter
            sort_by: Sort criteria for recommendations
        """
        target_quarter = target_quarter or self.config_manager.get_current_quarter()
        recommendations = self.get_quarterly_recommendations(location, target_quarter, 15)
        
        # Get contextual information
        region_info = self.config_manager.get_region(location)
        quarter_info = self.config_manager.get_quarters()[target_quarter]
        economic_factors = self.config_manager.get_economic_factors()
        
        # Print enhanced header
        print(f"\n{'='*90}")
        print(f"🏪 QUARTERLY INVENTORY RECOMMENDATIONS FOR {location.upper()}")
        print(f"📅 Target Quarter: {target_quarter} ({quarter_info.description})")
        print(f"🌤️  Season: {quarter_info.season.replace('_', ' ').title()}")
        print(f"👥 Population: {region_info.population:,} | Work: {', '.join(region_info.dominant_work[:3])}")
        print(f"🏢 Key Venues: {region_info.enhanced_key_locations.get('churches', 0)} churches, "
              f"{region_info.enhanced_key_locations.get('schools', 0)} schools")
        print(f"📊 Sorted by: {sort_by.replace('_', ' ').title()}")
        print(f"💱 USD/GHS Rate: {economic_factors.usd_to_cedis_rate:.2f} | "
              f"Inflation: {economic_factors.quarterly_inflation_projection[target_quarter]:.1%}")
        print(f"🎯 Holiday Boost: {quarter_info.holiday_multiplier}x")
        print(f"{'='*90}")
        
        # Sort recommendations
        if sort_by == 'quarterly_profit_potential':
            recommendations.sort(key=lambda x: x.analysis.financial_projection.estimated_monthly_profit_cedis * 3, reverse=True)
        elif sort_by == 'profit_margin':
            recommendations.sort(key=lambda x: float(x.analysis.financial_projection.profit_margin_percent.replace('%', '')), reverse=True)
        elif sort_by == 'sale_time_days':
            recommendations.sort(key=lambda x: x.analysis.financial_projection.sale_time_days, reverse=False)
        elif sort_by == 'category':
            recommendations.sort(key=lambda x: x.category)
        
        # Group by category for better presentation
        categories = {}
        for rec in recommendations:
            cat = rec.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(rec)
        
        rank = 1
        for category, items in categories.items():
            print(f"\n🔷 {category.upper()}")
            print("-" * 60)
            
            for rec in items:
                analysis = rec.analysis
                financial = analysis.financial_projection
                
                print(f"{rank:2d}. 📦 {rec.product}")
                print(f"    ⭐ Business Score: {rec.business_score:.1f}/10")
                print(f"    💰 Cost: ¢{financial.cost_price_cedis:.2f} → Sell: ¢{financial.selling_price_cedis:.2f} "
                      f"(Margin: {financial.profit_margin_percent})")
                print(f"    📈 Quarterly Potential: ¢{financial.estimated_monthly_profit_cedis * 3:.2f} profit | "
                      f"¢{financial.estimated_monthly_revenue_cedis * 3:.2f} revenue")
                print(f"    ⏱️  Sale Time: {financial.sale_time_days} days | "
                      f"Shelf Life: {financial.perishability_days} days")
                
                # Check if product is imported
                product_data = None
                for pid, pdata in self.config_manager.get_products().items():
                    if pdata.name == rec.product:
                        product_data = pdata
                        break
                
                if product_data and product_data.import_dependent:
                    print(f"    🌍 Import Status: Currency-sensitive pricing")
                else:
                    print(f"    🇬🇭 Local Product: Stable local pricing")
                
                print(f"    ✅ Customer Benefit: {analysis.customer_benefit}")
                print(f"    📊 Analysis: {analysis.reasoning}")
                
                if analysis.risk_factors:
                    print(f"    ⚠️  Risks: {', '.join(analysis.risk_factors[:2])}...")
                
                print()
                rank += 1
                
                if rank > 15:  # Limit display
                    break
            
            if rank > 15:
                break
        
        # Print quarterly insights
        self._print_quarterly_insights(target_quarter, recommendations)
    
    def _print_quarterly_insights(self, quarter: str, recommendations: List[ProductRecommendation]) -> None:
        """Print quarterly market insights."""
        print(f"\n{'='*60}")
        print(f"💡 {quarter} MARKET INSIGHTS")
        print(f"{'='*60}")
        
        # Category analysis
        category_scores = {}
        for rec in recommendations:
            if rec.category not in category_scores:
                category_scores[rec.category] = []
            category_scores[rec.category].append(rec.business_score)
        
        best_categories = []
        for cat, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            best_categories.append((cat, avg_score))
        
        best_categories.sort(key=lambda x: x[1], reverse=True)
        
        print(f"🏆 Top Performing Categories:")
        print("-" * 30)
        for i, (category, score) in enumerate(best_categories[:3], 1):
            print(f"  {i}. {category} - {score:.1f}/10 average")
        
        # Risk analysis
        high_risk_count = sum(1 for rec in recommendations if rec.business_score < 6)
        low_risk_count = sum(1 for rec in recommendations if rec.business_score >= 8)
        
        print(f"\n⚖️  Risk Profile:")
        print("-" * 20)
        print(f"  • Low Risk Products: {low_risk_count}")
        print(f"  • High Risk Products: {high_risk_count}")
        
        # Economic impact
        total_potential = sum(rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3 
                            for rec in recommendations)
        
        print(f"\n💰 Economic Impact:")
        print("-" * 20)
        print(f"  • Total Quarterly Profit Potential: ¢{total_potential:,.2f}")
        print(f"  • Average Score: {sum(rec.business_score for rec in recommendations) / len(recommendations):.1f}/10")
        
        # Quarter-specific advice
        quarter_advice = {
            'Q1': "🎯 Focus on Independence Day items and school preparations",
            'Q2': "🌧️ Rainy season - prioritize indoor and farming-related products", 
            'Q3': "📚 Back-to-school peak - education supplies and young professional items",
            'Q4': "🎄 Christmas boom - cultural goods, gifts, and celebration items"
        }
        
        print(f"\n{quarter_advice.get(quarter, '🔍 General business focus recommended')}")
        print(f"{'='*60}\n")
    
    def generate_quarterly_report(self, 
                                locations: List[str], 
                                target_quarter: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive quarterly business report for multiple locations.
        
        Args:
            locations: List of location names to analyze
            target_quarter: Target quarter (Q1-Q4), defaults to current quarter
        
        Returns:
            Dictionary containing comprehensive quarterly analysis
        """
        target_quarter = target_quarter or self.config_manager.get_current_quarter()
        quarter_info = self.config_manager.get_quarters()[target_quarter]
        economic_factors = self.config_manager.get_economic_factors()
        
        report = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'target_quarter': target_quarter,
            'quarter_description': quarter_info.description,
            'season': quarter_info.season,
            'holiday_multiplier': quarter_info.holiday_multiplier,
            'key_events': quarter_info.events,
            'economic_factors': {
                'inflation_rate': economic_factors.quarterly_inflation_projection[target_quarter],
                'usd_cedis_rate': economic_factors.usd_to_cedis_rate,
                'currency_volatility': economic_factors.currency_volatility
            },
            'locations': {},
            'cross_location_insights': {}
        }
        
        all_recommendations = {}
        
        for location in locations:
            if location in self.config_manager.get_regions():
                recommendations = self.get_quarterly_recommendations(location, target_quarter, 10)
                region_info = self.config_manager.get_region(location)
                
                # Calculate category distribution
                category_summary = {}
                for rec in recommendations:
                    cat = rec.category
                    if cat not in category_summary:
                        category_summary[cat] = {'count': 0, 'avg_score': 0, 'total_profit_potential': 0}
                    category_summary[cat]['count'] += 1
                    category_summary[cat]['avg_score'] += rec.business_score
                    category_summary[cat]['total_profit_potential'] += rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3
                
                for cat in category_summary:
                    category_summary[cat]['avg_score'] /= category_summary[cat]['count']
                    category_summary[cat]['avg_score'] = round(category_summary[cat]['avg_score'], 2)
                
                # Economic impact analysis
                imported_products = []
                local_products = []
                
                for rec in recommendations:
                    product_data = None
                    for pid, pdata in self.config_manager.get_products().items():
                        if pdata.name == rec.product:
                            product_data = pdata
                            break
                    
                    if product_data:
                        if product_data.import_dependent:
                            imported_products.append(rec)
                        else:
                            local_products.append(rec)
                
                report['locations'][location] = {
                    'region_info': {
                        'type': region_info.region_type.replace('_', ' ').title(),
                        'population': f"{region_info.population:,}",
                        'economic_base': region_info.dominant_work,
                        'infrastructure_score': round(
                            (region_info.infrastructure.electricity_reliability +
                             region_info.infrastructure.cold_storage_access +
                             region_info.infrastructure.transport_quality) / 3, 2
                        ),
                        'key_venues': {
                            'churches': region_info.enhanced_key_locations.get('churches', 0),
                            'schools': region_info.enhanced_key_locations.get('schools', 0),
                            'companies': region_info.enhanced_key_locations.get('companies', 0),
                            'markets': region_info.enhanced_key_locations.get('markets', 0)
                        }
                    },
                    'category_summary': category_summary,
                    'top_recommendations': [
                        {
                            'product': rec.product,
                            'category': rec.category,
                            'business_score': rec.business_score,
                            'quarterly_profit_potential': rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3,
                            'risk_level': 'Low' if rec.business_score >= 8 else 'Medium' if rec.business_score >= 6 else 'High'
                        }
                        for rec in recommendations[:5]
                    ],
                    'economic_analysis': {
                        'total_profit_potential': sum(rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3 for rec in recommendations),
                        'avg_business_score': round(sum(rec.business_score for rec in recommendations) / len(recommendations), 2),
                        'imported_products_count': len(imported_products),
                        'local_products_count': len(local_products),
                        'currency_risk_exposure': round(
                            sum(rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3 for rec in imported_products) /
                            sum(rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3 for rec in recommendations) * 100, 1
                        ) if recommendations else 0
                    }
                }
                
                all_recommendations[location] = recommendations
        
        # Cross-location insights
        if len(locations) > 1:
            # Find best opportunities across locations
            best_opportunities = {}
            for location, recs in all_recommendations.items():
                for rec in recs:
                    if rec.product not in best_opportunities:
                        best_opportunities[rec.product] = {}
                    best_opportunities[rec.product][location] = rec.business_score
            
            # Market insights
            location_rankings = []
            for location in locations:
                if location in report['locations']:
                    location_rankings.append((
                        location,
                        report['locations'][location]['economic_analysis']['avg_business_score']
                    ))
            
            location_rankings.sort(key=lambda x: x[1], reverse=True)
            
            report['cross_location_insights'] = {
                'best_overall_market': location_rankings[0][0] if location_rankings else None,
                'market_rankings': location_rankings,
                'universal_opportunities': [
                    {
                        'product': product,
                        'locations': list(scores.keys()),
                        'avg_score': round(sum(scores.values()) / len(scores), 2),
                        'best_location': max(scores.items(), key=lambda x: x[1])
                    }
                    for product, scores in best_opportunities.items()
                    if len(scores) >= len(locations) * 0.8  # Present in 80%+ of locations
                ][:5],
                'regional_specializations': self._identify_regional_specializations(all_recommendations)
            }
        
        return report
    
    def _identify_regional_specializations(self, all_recommendations: Dict[str, List[ProductRecommendation]]) -> List[Dict]:
        """Identify what each region specializes in."""
        specializations = []
        
        # Calculate category averages by location
        location_category_scores = {}
        for location, recommendations in all_recommendations.items():
            location_category_scores[location] = {}
            category_scores = {}
            
            for rec in recommendations:
                if rec.category not in category_scores:
                    category_scores[rec.category] = []
                category_scores[rec.category].append(rec.business_score)
            
            for category, scores in category_scores.items():
                location_category_scores[location][category] = sum(scores) / len(scores)
        
        # Find where each location excels
        for location in all_recommendations.keys():
            best_categories = []
            for category, score in location_category_scores[location].items():
                # Check if this location is significantly better than others for this category
                other_scores = []
                for other_location in all_recommendations.keys():
                    if other_location != location and category in location_category_scores[other_location]:
                        other_scores.append(location_category_scores[other_location][category])
                
                if other_scores:
                    avg_others = sum(other_scores) / len(other_scores)
                    if score > avg_others + 0.5:  # At least 0.5 points better
                        best_categories.append({
                            'category': category.replace('_', ' ').title(),
                            'score': round(score, 2),
                            'advantage': round(score - avg_others, 2)
                        })
            
            if best_categories:
                best_categories.sort(key=lambda x: x['advantage'], reverse=True)
                specializations.append({
                    'location': location,
                    'specializations': best_categories[:3]  # Top 3 specializations
                })
        
        return specializations
    
    def export_quarterly_analysis(self, 
                                locations: List[str],
                                output_path: str,
                                target_quarter: str = None,
                                format_type: str = 'json') -> None:
        """
        Export quarterly analysis to file.
        
        Args:
            locations: List of locations to analyze
            output_path: Output file path
            target_quarter: Target quarter for analysis
            format_type: Export format ('json' or 'csv')
        """
        report = self.generate_quarterly_report(locations, target_quarter)
        
        try:
            if format_type.lower() == 'json':
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                    
            elif format_type.lower() == 'csv':
                # Flatten data for CSV export
                csv_rows = []
                for location, data in report['locations'].items():
                    for rec in data['top_recommendations']:
                        row = {
                            'analysis_date': report['analysis_date'],
                            'quarter': report['target_quarter'],
                            'location': location,
                            'region_type': data['region_info']['type'],
                            'population': data['region_info']['population'],
                            'product': rec['product'],
                            'category': rec['category'],
                            'business_score': rec['business_score'],
                            'quarterly_profit_potential': rec['quarterly_profit_potential'],
                            'risk_level': rec['risk_level'],
                            'infrastructure_score': data['region_info']['infrastructure_score'],
                            'currency_risk_exposure': data['economic_analysis']['currency_risk_exposure']
                        }
                        csv_rows.append(row)
                
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if csv_rows:
                        writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
                        writer.writeheader()
                        writer.writerows(csv_rows)
            
            self.logger.info(f"Quarterly analysis exported to {format_type.upper()}: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting quarterly analysis: {e}")
            raise
    
    # Enhanced existing methods
    def print_recommendations_console(self,
                                    results: Dict[str, List[ProductRecommendation]],
                                    target_month: int) -> None:
        """
        Print formatted recommendations to console with quarterly context.
        
        Args:
            results: Dictionary mapping location names to recommendations
            target_month: Target month for the analysis
        """
        # Convert month to quarter for enhanced context
        target_quarter = f"Q{(target_month - 1) // 3 + 1}"
        
        for location, recommendations in results.items():
            region_data = self.config_manager.get_region(location)
            quarter_info = self.config_manager.get_quarters()[target_quarter]
            
            # Enhanced console output with quarterly context
            self.formatter.print_location_recommendations_with_quarterly_context(
                location=location,
                recommendations=recommendations,
                region_data=region_data,
                target_month=target_month,
                quarter_info=quarter_info
            )
    
    def compare_locations_quarterly(self, 
                                  locations: List[str], 
                                  target_quarter: str = None,
                                  product_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced location comparison with quarterly intelligence.
        
        Args:
            locations: List of location names to compare
            target_quarter: Target quarter for analysis
            product_filter: Optional product category filter
        
        Returns:
            Dictionary containing enhanced comparative analysis
        """
        if len(locations) < 2:
            raise ValueError("Need at least 2 locations for comparison")
        
        target_quarter = target_quarter or self.config_manager.get_current_quarter()
        
        # Validate all locations exist
        for location in locations:
            if not self.config_manager.get_region(location):
                raise ValueError(f"Location '{location}' not found")
        
        comparison_data = {
            'analysis_info': {
                'quarter': target_quarter,
                'quarter_description': self.config_manager.get_quarters()[target_quarter].description,
                'locations_compared': locations,
                'filter_applied': product_filter or 'None'
            },
            'locations': {},
            'best_opportunities': {},
            'market_insights': {},
            'quarterly_insights': {}
        }
        
        # Get quarterly recommendations for each location
        all_recommendations = {}
        for location in locations:
            recommendations = self.get_quarterly_recommendations(location, target_quarter, 10)
            
            # Filter by product category if specified
            if product_filter:
                recommendations = [
                    rec for rec in recommendations 
                    if product_filter.lower() in rec.category.lower()
                ]
            
            all_recommendations[location] = recommendations
            region_data = self.config_manager.get_region(location)
            
            # Enhanced location data
            comparison_data['locations'][location] = {
                'quarterly_top_score': recommendations[0].business_score if recommendations else 0,
                'quarterly_average_score': round(sum(rec.business_score for rec in recommendations) / len(recommendations), 2) if recommendations else 0,
                'best_quarterly_product': recommendations[0].product if recommendations else None,
                'population': region_data.population,
                'income_level': region_data.income_level,
                'infrastructure_score': round((
                    region_data.infrastructure.electricity_reliability +
                    region_data.infrastructure.cold_storage_access +
                    region_data.infrastructure.transport_quality
                ) / 3, 2),
                'quarterly_profit_potential': sum(
                    rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3 
                    for rec in recommendations
                ),
                'dominant_work': region_data.dominant_work,
                'key_venues_count': sum([
                    region_data.enhanced_key_locations.get('churches', 0),
                    region_data.enhanced_key_locations.get('schools', 0),
                    region_data.enhanced_key_locations.get('companies', 0),
                    region_data.enhanced_key_locations.get('markets', 0)
                ])
            }
        
        # Enhanced opportunity analysis
        self._analyze_cross_location_opportunities(comparison_data, all_recommendations)
        
        # Enhanced market insights
        self._generate_enhanced_market_insights(comparison_data, target_quarter)
        
        return comparison_data
    
    def _analyze_cross_location_opportunities(self, 
                                           comparison_data: Dict[str, Any], 
                                           all_recommendations: Dict[str, List[ProductRecommendation]]) -> None:
        """Analyze opportunities across locations."""
        all_products = set()
        for recommendations in all_recommendations.values():
            for rec in recommendations:
                all_products.add(rec.product)
        
        for product in all_products:
            product_scores = {}
            for location, recommendations in all_recommendations.items():
                for rec in recommendations:
                    if rec.product == product:
                        product_scores[location] = {
                            'business_score': rec.business_score,
                            'quarterly_profit': rec.analysis.financial_projection.estimated_monthly_profit_cedis * 3
                        }
                        break
            
            if product_scores:
                best_location = max(product_scores.items(), key=lambda x: x[1]['business_score'])
                comparison_data['best_opportunities'][product] = {
                    'best_location': best_location[0],
                    'best_score': best_location[1]['business_score'],
                    'best_quarterly_profit': best_location[1]['quarterly_profit'],
                    'location_performance': product_scores
                }
    
    def _generate_enhanced_market_insights(self, 
                                         comparison_data: Dict[str, Any], 
                                         target_quarter: str) -> None:
        """Generate enhanced market insights."""
        location_data = comparison_data['locations']
        
        # Standard insights
        best_overall = max(location_data.items(), key=lambda x: x[1]['quarterly_average_score'])
        highest_potential = max(location_data.items(), key=lambda x: x[1]['quarterly_top_score'])
        largest_market = max(location_data.items(), key=lambda x: x[1]['population'])
        most_profitable = max(location_data.items(), key=lambda x: x[1]['quarterly_profit_potential'])
        
        comparison_data['market_insights'] = {
            'best_overall_quarterly_location': best_overall[0],
            'highest_potential_location': highest_potential[0],
            'largest_market': largest_market[0],
            'most_profitable_quarterly': most_profitable[0],
            'comparison_summary': f"Analyzed {len(location_data)} locations for {target_quarter}"
        }
        
        # Quarterly-specific insights
        quarter_insights = {
            'Q1': 'Independence Day preparations and school resumption create opportunities',
            'Q2': 'Rainy season farming activities drive rural demand',
            'Q3': 'Back-to-school peak maximizes education and youth-focused products',
            'Q4': 'Christmas season multiplier creates exceptional profit opportunities'
        }
        
        comparison_data['quarterly_insights'] = {
            'season_description': quarter_insights.get(target_quarter, 'Standard business season'),
            'economic_context': {
                'inflation_rate': self.config_manager.get_economic_factors().quarterly_inflation_projection[target_quarter],
                'holiday_multiplier': self.config_manager.get_quarters()[target_quarter].holiday_multiplier,
                'key_events': self.config_manager.get_quarters()[target_quarter].events
            },
            'strategic_recommendations': self._generate_quarterly_strategy(target_quarter, location_data)
        }
    
    def _generate_quarterly_strategy(self, quarter: str, location_data: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations for the quarter."""
        strategies = []
        
        # Quarter-specific strategies
        if quarter == 'Q1':
            strategies.extend([
                "Focus on Independence Day celebrations and national pride items",
                "Prepare for school resumption with education supplies",
                "Leverage end of Harmattan season for health and wellness products"
            ])
        elif quarter == 'Q2':
            strategies.extend([
                "Target farming communities with agricultural supplies",
                "Indoor products gain importance during rainy season",
                "Easter celebrations create gift-giving opportunities"
            ])
        elif quarter == 'Q3':
            strategies.extend([
                "Maximize back-to-school demand for education products",
                "Young professional and student-focused items perform well",
                "Agricultural productivity season supports rural markets"
            ])
        elif quarter == 'Q4':
            strategies.extend([
                "Christmas season multiplier maximizes cultural goods and gifts",
                "Harvest celebrations support food and celebration items",
                "End-of-year purchasing drives premium product demand"
            ])
        
        # Location-specific strategies based on performance
        best_performer = max(location_data.items(), key=lambda x: x[1]['quarterly_average_score'])
        strategies.append(f"Consider {best_performer[0]} as priority market with {best_performer[1]['quarterly_average_score']:.1f}/10 average score")
        
        return strategies