"""
Ghana Inventory Recommendation System - Main Recommender Class

Provides business-focused inventory recommendations for Ghanaian locations.
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
    RegionData, ProductData
)
from .calculators.business_score_calculator import BusinessScoreCalculator
from .utils.formatters import RecommendationFormatter


class GhanaInventoryRecommender:
    """
    Main class for generating inventory recommendations for Ghana market.
    
    Provides comprehensive business analysis including profitability,
    demand potential, risk assessment, and infrastructure compatibility.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the recommender with configuration data.
        
        Args:
            config_manager: Configured instance of ConfigManager
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # Initialize business score calculator
        self.score_calculator = BusinessScoreCalculator(
            config_manager.get_holiday_periods(),
            config_manager.get_scoring_weights(),
            config_manager.get_business_parameters()
        )
        
        # Initialize formatter
        self.formatter = RecommendationFormatter()
        
        self.logger.info("Ghana Inventory Recommender initialized successfully")
    
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
    
    def print_recommendations_console(self,
                                    results: Dict[str, List[ProductRecommendation]],
                                    target_month: int) -> None:
        """
        Print formatted recommendations to console.
        
        Args:
            results: Dictionary mapping location names to recommendations
            target_month: Target month for the analysis
        """
        for location, recommendations in results.items():
            region_data = self.config_manager.get_region(location)
            self.formatter.print_location_recommendations(
                location=location,
                recommendations=recommendations,
                region_data=region_data,
                target_month=target_month
            )
    
    def export_recommendations_json(self,
                                  results: Dict[str, List[ProductRecommendation]],
                                  output_path: str,
                                  target_month: int) -> None:
        """
        Export recommendations to JSON file.
        
        Args:
            results: Dictionary mapping location names to recommendations
            output_path: Path for the output JSON file
            target_month: Target month for the analysis
        """
        try:
            export_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'target_month': target_month,
                    'month_name': datetime(2024, target_month, 1).strftime('%B'),
                    'locations_analyzed': list(results.keys()),
                    'total_recommendations': sum(len(recs) for recs in results.values())
                },
                'recommendations': {}
            }
            
            for location, recommendations in results.items():
                region_data = self.config_manager.get_region(location)
                export_data['recommendations'][location] = {
                    'region_info': {
                        'population': region_data.population,
                        'income_level': region_data.income_level,
                        'region_type': region_data.region_type,
                        'dominant_work': region_data.dominant_work
                    },
                    'products': [rec.to_dict() for rec in recommendations]
                }
            
            # Write to file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Recommendations exported to JSON: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_recommendations_csv(self,
                                 results: Dict[str, List[ProductRecommendation]],
                                 output_path: str,
                                 target_month: int) -> None:
        """
        Export recommendations to CSV file.
        
        Args:
            results: Dictionary mapping location names to recommendations
            output_path: Path for the output CSV file
            target_month: Target month for the analysis
        """
        try:
            # Prepare CSV data
            csv_rows = []
            
            for location, recommendations in results.items():
                region_data = self.config_manager.get_region(location)
                
                for i, rec in enumerate(recommendations, 1):
                    financial = rec.analysis.financial_projection
                    
                    row = {
                        'location': location,
                        'region_type': region_data.region_type,
                        'population': region_data.population,
                        'rank': i,
                        'product_name': rec.product,
                        'category': rec.category,
                        'business_score': rec.business_score,
                        'cost_price_cedis': financial.cost_price_cedis,
                        'selling_price_cedis': financial.selling_price_cedis,
                        'profit_margin_percent': financial.profit_margin_percent,
                        'estimated_monthly_revenue_cedis': financial.estimated_monthly_revenue_cedis,
                        'estimated_monthly_profit_cedis': financial.estimated_monthly_profit_cedis,
                        'sale_time_days': financial.sale_time_days,
                        'perishability_days': financial.perishability_days,
                        'customer_benefit': rec.analysis.customer_benefit,
                        'risk_factors': '; '.join(rec.analysis.risk_factors),
                        'reasoning': rec.analysis.reasoning,
                        'target_month': target_month
                    }
                    csv_rows.append(row)
            
            # Write CSV file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if csv_rows:
                    writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_rows)
            
            self.logger.info(f"Recommendations exported to CSV: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def get_location_summary(self, location: str) -> Dict[str, Any]:
        """
        Get comprehensive summary for a specific location.
        
        Args:
            location: Name of the location
        
        Returns:
            Dictionary containing location analysis summary
        """
        region_data = self.config_manager.get_region(location)
        if not region_data:
            raise ValueError(f"Location '{location}' not found")
        
        # Get current recommendations
        current_recommendations = self.get_recommendations(location, 10)
        
        # Calculate category performance
        category_performance = {}
        products_by_category = {}
        
        for rec in current_recommendations:
            category = rec.category
            if category not in category_performance:
                category_performance[category] = []
                products_by_category[category] = []
            
            category_performance[category].append(rec.business_score)
            products_by_category[category].append(rec.product)
        
        # Calculate averages
        category_averages = {
            cat: round(sum(scores) / len(scores), 2)
            for cat, scores in category_performance.items()
        }
        
        return {
            'location': location,
            'region_data': {
                'type': region_data.region_type,
                'population': region_data.population,
                'income_level': region_data.income_level,
                'dominant_work': region_data.dominant_work,
                'electricity_reliability': region_data.infrastructure.electricity_reliability,
                'cold_storage_access': region_data.infrastructure.cold_storage_access,
                'transport_quality': region_data.infrastructure.transport_quality
            },
            'top_recommendations': [
                {
                    'product': rec.product,
                    'score': rec.business_score,
                    'monthly_profit': rec.analysis.financial_projection.estimated_monthly_profit_cedis
                }
                for rec in current_recommendations[:5]
            ],
            'category_performance': category_averages,
            'best_categories': sorted(category_averages.items(), key=lambda x: x[1], reverse=True)[:3],
            'total_products_analyzed': len(self.config_manager.get_products()),
            'analysis_date': datetime.now().isoformat()
        }
    
    def compare_locations(self, locations: List[str], product_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare multiple locations for business opportunities.
        
        Args:
            locations: List of location names to compare
            product_filter: Optional product category filter
        
        Returns:
            Dictionary containing comparative analysis
        """
        if len(locations) < 2:
            raise ValueError("Need at least 2 locations for comparison")
        
        # Validate all locations exist
        for location in locations:
            if not self.config_manager.get_region(location):
                raise ValueError(f"Location '{location}' not found")
        
        comparison_data = {
            'locations': {},
            'best_opportunities': {},
            'market_insights': {}
        }
        
        # Get recommendations for each location
        for location in locations:
            recommendations = self.get_recommendations(location, 10)
            
            # Filter by product category if specified
            if product_filter:
                recommendations = [
                    rec for rec in recommendations 
                    if product_filter.lower() in rec.category.lower()
                ]
            
            region_data = self.config_manager.get_region(location)
            
            comparison_data['locations'][location] = {
                'top_score': recommendations[0].business_score if recommendations else 0,
                'average_score': round(sum(rec.business_score for rec in recommendations) / len(recommendations), 2) if recommendations else 0,
                'best_product': recommendations[0].product if recommendations else None,
                'population': region_data.population,
                'income_level': region_data.income_level,
                'infrastructure_score': round((
                    region_data.infrastructure.electricity_reliability +
                    region_data.infrastructure.cold_storage_access +
                    region_data.infrastructure.transport_quality
                ) / 3, 2)
            }
        
        # Find best opportunities across locations
        all_products = set()
        for location in locations:
            recommendations = self.get_recommendations(location, 10)
            if product_filter:
                recommendations = [
                    rec for rec in recommendations 
                    if product_filter.lower() in rec.category.lower()
                ]
            for rec in recommendations:
                all_products.add(rec.product)
        
        for product in all_products:
            product_scores = {}
            for location in locations:
                recommendations = self.get_recommendations(location, 10)
                if product_filter:
                    recommendations = [
                        rec for rec in recommendations 
                        if product_filter.lower() in rec.category.lower()
                    ]
                for rec in recommendations:
                    if rec.product == product:
                        product_scores[location] = rec.business_score
                        break
            
            if product_scores:
                best_location = max(product_scores.items(), key=lambda x: x[1])
                comparison_data['best_opportunities'][product] = {
                    'best_location': best_location[0],
                    'best_score': best_location[1],
                    'location_scores': product_scores
                }
        
        # Market insights
        location_data = comparison_data['locations']
        best_overall = max(location_data.items(), key=lambda x: x[1]['average_score'])
        highest_potential = max(location_data.items(), key=lambda x: x[1]['top_score'])
        largest_market = max(location_data.items(), key=lambda x: x[1]['population'])
        
        comparison_data['market_insights'] = {
            'best_overall_location': best_overall[0],
            'highest_potential_location': highest_potential[0],
            'largest_market': largest_market[0],
            'comparison_summary': f"Analyzed {len(locations)} locations for {len(all_products)} products"
        }
        
        return comparison_data