"""
Web Application Server for Ghana Inventory Recommendation System
================================================================

Run this file to start the web dashboard:
python app.py

Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Import our existing system
from src.config_manager import ConfigManager
from src.inventory_recommender import GhanaInventoryRecommender
from src.utils.logger import setup_logger

# Initialize Flask app
app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')
CORS(app)  # Enable CORS for API calls

# Setup logging
logger = setup_logger('web_app', 'INFO')

# Initialize the recommendation system
try:
    config_path = Path('data/ghana_market_data.json')
    config_manager = ConfigManager(config_path)
    recommender = GhanaInventoryRecommender(config_manager)
    logger.info("Recommendation system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize recommendation system: {e}")
    recommender = None

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/regions')
def get_regions():
    """Get all available regions."""
    try:
        if not recommender:
            return jsonify({'error': 'System not initialized'}), 500
        
        regions = config_manager.get_regions()
        region_data = {}
        
        for name, region in regions.items():
            region_data[name] = {
                'name': name,
                'population': region.population,
                'income_level': region.income_level,
                'region_type': region.region_type,
                'infrastructure': {
                    'electricity_reliability': region.infrastructure.electricity_reliability,
                    'cold_storage_access': region.infrastructure.cold_storage_access,
                    'transport_quality': region.infrastructure.transport_quality
                }
            }
        
        return jsonify(region_data)
    
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations')
def get_recommendations():
    """Get recommendations for a specific location and parameters."""
    try:
        if not recommender:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Get parameters from request
        location = request.args.get('location', 'Accra')
        month = int(request.args.get('month', datetime.now().month))
        num_recommendations = int(request.args.get('limit', 10))
        category_filter = request.args.get('category', 'all')
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            location=location,
            num_recommendations=num_recommendations,
            target_month=month
        )
        
        # Filter by category if specified
        if category_filter != 'all':
            recommendations = [
                rec for rec in recommendations 
                if category_filter.lower() in rec.category.lower()
            ]
        
        # Convert to JSON-serializable format
        result = []
        for rec in recommendations:
            result.append({
                'product': rec.product,
                'category': rec.category,
                'business_score': rec.business_score,
                'monthly_profit': rec.analysis.financial_projection.estimated_monthly_profit_cedis,
                'monthly_revenue': rec.analysis.financial_projection.estimated_monthly_revenue_cedis,
                'cost_price': rec.analysis.financial_projection.cost_price_cedis,
                'selling_price': rec.analysis.financial_projection.selling_price_cedis,
                'profit_margin': rec.analysis.financial_projection.profit_margin_percent,
                'sale_time_days': rec.analysis.financial_projection.sale_time_days,
                'perishability_days': rec.analysis.financial_projection.perishability_days,
                'customer_benefit': rec.analysis.customer_benefit,
                'risk_factors': rec.analysis.risk_factors,
                'reasoning': rec.analysis.reasoning,
                'detailed_scores': rec.analysis.detailed_scores
            })
        
        return jsonify({
            'location': location,
            'month': month,
            'recommendations': result,
            'total_count': len(result)
        })
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/comparison')
def get_location_comparison():
    """Compare multiple locations."""
    try:
        if not recommender:
            return jsonify({'error': 'System not initialized'}), 500
        
        locations = request.args.getlist('locations')
        if not locations:
            locations = ['Accra', 'Kumasi', 'Tamale', 'Cape Coast']
        
        month = int(request.args.get('month', datetime.now().month))
        
        comparison_data = {}
        
        for location in locations:
            try:
                recommendations = recommender.get_recommendations(location, 10, month)
                region_data = config_manager.get_region(location)
                
                if recommendations:
                    avg_score = sum(rec.business_score for rec in recommendations) / len(recommendations)
                    total_profit = sum(
                        rec.analysis.financial_projection.estimated_monthly_profit_cedis 
                        for rec in recommendations
                    )
                    best_product = recommendations[0].product
                    best_score = recommendations[0].business_score
                else:
                    avg_score = 0
                    total_profit = 0
                    best_product = "No recommendations"
                    best_score = 0
                
                comparison_data[location] = {
                    'location': location,
                    'population': region_data.population,
                    'income_level': region_data.income_level,
                    'avg_score': round(avg_score, 2),
                    'total_profit': round(total_profit, 2),
                    'best_product': best_product,
                    'best_score': round(best_score, 2),
                    'infrastructure_score': round((
                        region_data.infrastructure.electricity_reliability +
                        region_data.infrastructure.cold_storage_access +
                        region_data.infrastructure.transport_quality
                    ) / 3, 2)
                }
            
            except Exception as loc_error:
                logger.warning(f"Error processing {location}: {loc_error}")
                continue
        
        return jsonify(comparison_data)
    
    except Exception as e:
        logger.error(f"Error in location comparison: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data for charts."""
    try:
        if not recommender:
            return jsonify({'error': 'System not initialized'}), 500
        
        location = request.args.get('location', 'Accra')
        month = int(request.args.get('month', datetime.now().month))
        
        recommendations = recommender.get_recommendations(location, 20, month)
        
        # Category performance
        category_performance = {}
        for rec in recommendations:
            category = rec.category
            if category not in category_performance:
                category_performance[category] = {
                    'scores': [],
                    'profits': [],
                    'count': 0
                }
            
            category_performance[category]['scores'].append(rec.business_score)
            category_performance[category]['profits'].append(
                rec.analysis.financial_projection.estimated_monthly_profit_cedis
            )
            category_performance[category]['count'] += 1
        
        # Calculate averages
        category_data = []
        for category, data in category_performance.items():
            category_data.append({
                'category': category,
                'avg_score': round(sum(data['scores']) / len(data['scores']), 2),
                'total_profit': round(sum(data['profits']), 2),
                'count': data['count']
            })
        
        # Risk distribution
        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0}
        for rec in recommendations:
            # Determine risk level based on scores and factors
            if rec.business_score >= 8:
                risk = 'Low'
            elif rec.business_score >= 6:
                risk = 'Medium'
            else:
                risk = 'High'
            
            # Adjust based on risk factors count
            risk_factor_count = len(rec.analysis.risk_factors)
            if risk_factor_count > 3:
                risk = 'High'
            elif risk_factor_count > 1 and risk == 'Low':
                risk = 'Medium'
            
            risk_distribution[risk] += 1
        
        return jsonify({
            'category_performance': category_data,
            'risk_distribution': risk_distribution,
            'total_recommendations': len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_data():
    """Export recommendations data."""
    try:
        if not recommender:
            return jsonify({'error': 'System not initialized'}), 500
        
        location = request.args.get('location', 'Accra')
        month = int(request.args.get('month', datetime.now().month))
        format_type = request.args.get('format', 'json')
        
        recommendations = recommender.get_recommendations(location, 20, month)
        
        if format_type == 'json':
            # Export as JSON
            export_data = {
                'export_info': {
                    'location': location,
                    'month': month,
                    'generated_at': datetime.now().isoformat(),
                    'total_recommendations': len(recommendations)
                },
                'recommendations': [rec.to_dict() for rec in recommendations]
            }
            return jsonify(export_data)
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_products():
    """Search for products across all categories."""
    try:
        if not recommender:
            return jsonify({'error': 'System not initialized'}), 500
        
        query = request.args.get('q', '').lower()
        location = request.args.get('location', 'Accra')
        month = int(request.args.get('month', datetime.now().month))
        
        if not query:
            return jsonify({'results': []})
        
        recommendations = recommender.get_recommendations(location, 50, month)
        
        # Filter recommendations by search query
        results = []
        for rec in recommendations:
            if (query in rec.product.lower() or 
                query in rec.category.lower() or
                query in rec.analysis.customer_benefit.lower()):
                
                results.append({
                    'product': rec.product,
                    'category': rec.category,
                    'score': rec.business_score,
                    'monthly_profit': rec.analysis.financial_projection.estimated_monthly_profit_cedis,
                    'customer_benefit': rec.analysis.customer_benefit
                })
        
        return jsonify({'results': results[:20]})  # Limit to top 20 results
    
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🇬🇭 Ghana Inventory Recommendation System - Web Dashboard")
    print("=" * 60)
    print("Starting web server...")
    print("Dashboard URL: http://localhost:5000")
    print("API Base URL: http://localhost:5000/api/")
    print("=" * 60)
    print("Available endpoints:")
    print("• GET /                     - Main dashboard")
    print("• GET /api/regions          - Get all regions")
    print("• GET /api/recommendations  - Get recommendations")
    print("• GET /api/comparison       - Compare locations")
    print("• GET /api/analytics        - Get analytics data")
    print("• GET /api/export           - Export data")
    print("• GET /api/search           - Search products")
    print("=" * 60)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )