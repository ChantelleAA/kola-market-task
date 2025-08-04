"""
Formatting utilities for the Ghana Inventory Recommendation System.

Provides various output formatting options for recommendations.
"""

from datetime import datetime
from typing import List, Dict, Any

from ..models.market_data import ProductRecommendation, RegionData


class RecommendationFormatter:
    """Handles formatting of recommendation output."""
    
    def __init__(self):
        """Initialize the formatter."""
        pass
    
    def print_location_recommendations(self,
                                     location: str,
                                     recommendations: List[ProductRecommendation],
                                     region_data: RegionData,
                                     target_month: int) -> None:
        """
        Print formatted recommendations for a location to console.
        
        Args:
            location: Location name
            recommendations: List of product recommendations
            region_data: Region information
            target_month: Target month for analysis
        """
        month_name = datetime(2024, target_month, 1).strftime('%B')
        
        # Header
        print(f"\n{'='*80}")
        print(f"🏪 BUSINESS INVENTORY RECOMMENDATIONS FOR {location.upper()}")
        print(f"📅 Target Month: {month_name}")
        print(f"👥 Population: {region_data.population:,} | Income: {region_data.income_level}")
        print(f"🏢 Key Venues: {region_data.key_locations.get('churches', 0)} churches, "
              f"{region_data.key_locations.get('schools', 0)} schools, "
              f"{region_data.key_locations.get('companies', 0)} companies")
        print(f"{'='*80}")
        
        # Recommendations
        for i, rec in enumerate(recommendations, 1):
            self._print_single_recommendation(i, rec)
        
        # Summary
        if recommendations:
            avg_score = sum(rec.business_score for rec in recommendations) / len(recommendations)
            total_potential_profit = sum(
                rec.analysis.financial_projection.estimated_monthly_profit_cedis 
                for rec in recommendations
            )
            
            print(f"\n{'='*80}")
            print(f"📊 SUMMARY FOR {location.upper()}")
            print(f"Average Business Score: {avg_score:.1f}/10")
            print(f"Total Monthly Profit Potential: ¢{total_potential_profit:,.2f}")
            print(f"Recommendations Generated: {len(recommendations)}")
            print(f"{'='*80}\n")
    
    def _print_single_recommendation(self, rank: int, rec: ProductRecommendation) -> None:
        """Print a single recommendation with detailed formatting."""
        analysis = rec.analysis
        financial = analysis.financial_projection
        
        print(f"\n{rank}. 📦 {rec.product} ({rec.category})")
        print(f"   ⭐ Business Score: {rec.business_score}/10")
        
        # Financial info
        print(f"   💰 Cost: ¢{financial.cost_price_cedis} → Sell: ¢{financial.selling_price_cedis} "
              f"(Margin: {financial.profit_margin_percent})")
        
        # Projections
        print(f"   📈 Monthly Potential: ¢{financial.estimated_monthly_profit_cedis:,.2f} profit | "
              f"¢{financial.estimated_monthly_revenue_cedis:,.2f} revenue")
        
        # Timing
        print(f"   ⏱️  Sale Time: {financial.sale_time_days} days | "
              f"Shelf Life: {financial.perishability_days} days")
        
        # Benefits and analysis
        print(f"   ✅ Customer Benefit: {analysis.customer_benefit}")
        print(f"   📊 Analysis: {analysis.reasoning}")
        
        # Risk factors
        if analysis.risk_factors:
            risk_text = ', '.join(analysis.risk_factors)
            print(f"   ⚠️  Risks: {risk_text}")
    
    def format_comparison_table(self, comparison_data: Dict[str, Any]) -> str:
        """
        Format location comparison data as a readable table.
        
        Args:
            comparison_data: Comparison analysis data
        
        Returns:
            Formatted string representation
        """
        output = []
        output.append("="*80)
        output.append("📊 LOCATION COMPARISON ANALYSIS")
        output.append("="*80)
        
        # Location summary table
        output.append("\n🏘️  LOCATION OVERVIEW:")
        output.append("-" * 80)
        output.append(f"{'Location':<15} {'Population':<12} {'Income':<12} {'Top Score':<10} {'Avg Score':<10} {'Infra':<8}")
        output.append("-" * 80)
        
        for location, data in comparison_data['locations'].items():
            output.append(
                f"{location:<15} {data['population']:>11,} {data['income_level']:<12} "
                f"{data['top_score']:>9.1f} {data['average_score']:>9.1f} {data['infrastructure_score']:>7.1f}"
            )
        
        # Best opportunities
        output.append("\n🎯 BEST OPPORTUNITIES BY PRODUCT:")
        output.append("-" * 80)
        
        sorted_opportunities = sorted(
            comparison_data['best_opportunities'].items(),
            key=lambda x: x[1]['best_score'],
            reverse=True
        )
        
        for product, data in sorted_opportunities[:10]:  # Top 10
            output.append(f"• {product:<25} → {data['best_location']:<15} (Score: {data['best_score']:.1f})")
        
        # Market insights
        output.append("\n💡 MARKET INSIGHTS:")
        output.append("-" * 40)
        insights = comparison_data['market_insights']
        output.append(f"Best Overall Location: {insights['best_overall_location']}")
        output.append(f"Highest Potential: {insights['highest_potential_location']}")
        output.append(f"Largest Market: {insights['largest_market']}")
        output.append(f"Analysis Summary: {insights['comparison_summary']}")
        
        output.append("="*80)
        
        return "\n".join(output)
    
    def format_location_summary(self, summary_data: Dict[str, Any]) -> str:
        """
        Format location summary data as a readable report.
        
        Args:
            summary_data: Location summary data
        
        Returns:
            Formatted string representation
        """
        output = []
        location = summary_data['location']
        region = summary_data['region_data']
        
        output.append("="*60)
        output.append(f"📍 LOCATION ANALYSIS: {location.upper()}")
        output.append("="*60)
        
        # Region overview
        output.append("\n🏘️  REGION OVERVIEW:")
        output.append(f"Type: {region['type'].replace('_', ' ').title()}")
        output.append(f"Population: {region['population']:,}")
        output.append(f"Income Level: {region['income_level'].title()}")
        output.append(f"Primary Work: {', '.join(region['dominant_work'])}")
        
        # Infrastructure
        output.append("\n🏗️  INFRASTRUCTURE:")
        output.append(f"Electricity Reliability: {region['electricity_reliability']:.1%}")
        output.append(f"Cold Storage Access: {region['cold_storage_access']:.1%}")
        output.append(f"Transport Quality: {region['transport_quality']:.1%}")
        
        # Top recommendations
        output.append("\n🎯 TOP 5 RECOMMENDATIONS:")
        output.append("-" * 50)
        
        for i, rec in enumerate(summary_data['top_recommendations'], 1):
            output.append(
                f"{i}. {rec['product']:<25} Score: {rec['score']:>5.1f} "
                f"Profit: ¢{rec['monthly_profit']:>8.2f}"
            )
        
        # Category performance
        output.append("\n📊 CATEGORY PERFORMANCE:")
        output.append("-" * 40)
        
        for category, avg_score in summary_data['best_categories']:
            output.append(f"• {category:<25} {avg_score:>5.1f}/10")
        
        # Analysis metadata
        output.append(f"\n📅 Analysis Date: {summary_data['analysis_date'][:19]}")
        output.append(f"Products Analyzed: {summary_data['total_products_analyzed']}")
        
        output.append("="*60)
        
        return "\n".join(output)
    
    def format_json_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data for JSON export with proper structure.
        
        Args:
            data: Raw data dictionary
        
        Returns:
            Formatted dictionary suitable for JSON serialization
        """
        # Add metadata
        formatted = {
            'export_info': {
                'generated_at': datetime.now().isoformat(),
                'format_version': '2.0',
                'tool': 'Ghana Inventory Recommendation System'
            },
            'data': data
        }
        
        return formatted
    
    def create_executive_summary(self, 
                               location_results: Dict[str, List[ProductRecommendation]],
                               target_month: int) -> str:
        """
        Create an executive summary of all recommendations.
        
        Args:
            location_results: Results for all locations
            target_month: Target month for analysis
        
        Returns:
            Executive summary string
        """
        month_name = datetime(2024, target_month, 1).strftime('%B')
        
        output = []
        output.append("="*80)
        output.append("📋 EXECUTIVE SUMMARY - GHANA INVENTORY RECOMMENDATIONS")
        output.append(f"📅 Analysis Period: {month_name} 2024")
        output.append("="*80)
        
        # Overall statistics
        total_locations = len(location_results)
        total_recommendations = sum(len(recs) for recs in location_results.values())
        
        output.append(f"\n📊 ANALYSIS SCOPE:")
        output.append(f"• Locations Analyzed: {total_locations}")
        output.append(f"• Total Recommendations: {total_recommendations}")
        output.append(f"• Analysis Month: {month_name}")
        
        # Best opportunities across all locations
        all_recommendations = []
        for location, recommendations in location_results.items():
            for rec in recommendations:
                all_recommendations.append((location, rec))
        
        # Sort by business score
        all_recommendations.sort(key=lambda x: x[1].business_score, reverse=True)
        top_opportunities = all_recommendations[:5]
        
        output.append(f"\n🎯 TOP 5 BUSINESS OPPORTUNITIES:")
        output.append("-" * 60)
        
        for i, (location, rec) in enumerate(top_opportunities, 1):
            profit = rec.analysis.financial_projection.estimated_monthly_profit_cedis
            output.append(
                f"{i}. {rec.product} in {location} (Score: {rec.business_score:.1f}, "
                f"Profit: ¢{profit:.2f}/month)"
            )
        
        # Location rankings
        location_scores = {}
        for location, recommendations in location_results.items():
            if recommendations:
                avg_score = sum(rec.business_score for rec in recommendations) / len(recommendations)
                location_scores[location] = avg_score
        
        sorted_locations = sorted(location_scores.items(), key=lambda x: x[1], reverse=True)
        
        output.append(f"\n🏆 LOCATION RANKINGS (by average score):")
        output.append("-" * 40)
        
        for i, (location, avg_score) in enumerate(sorted_locations, 1):
            output.append(f"{i}. {location:<15} {avg_score:>5.1f}/10")
        
        # Category insights
        category_performance = {}
        for location, recommendations in location_results.items():
            for rec in recommendations:
                category = rec.category
                if category not in category_performance:
                    category_performance[category] = []
                category_performance[category].append(rec.business_score)
        
        category_averages = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_performance.items()
        }
        
        best_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
        
        output.append(f"\n📈 BEST PERFORMING CATEGORIES:")
        output.append("-" * 40)
        
        for i, (category, avg_score) in enumerate(best_categories[:5], 1):
            output.append(f"{i}. {category:<20} {avg_score:>5.1f}/10")
        
        # Recommendations
        output.append(f"\n💡 KEY RECOMMENDATIONS:")
        output.append("• Focus on top-scoring products for immediate profitability")
        output.append("• Consider seasonal timing for maximum impact")
        output.append("• Evaluate infrastructure requirements before implementation")
        output.append("• Monitor local competition and market conditions")
        
        output.append("\n" + "="*80)
        
        return "\n".join(output)