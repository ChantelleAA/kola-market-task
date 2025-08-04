#!/usr/bin/env python3
"""
Kola Market - Simple API Endpoint (Optional)
============================================

Optional simple API wrapper for the basic prototype.
Enables integration with WhatsApp bots, dashboards, mobile apps.

Usage:
    python simple_api.py
    
Test:
    curl http://localhost:5000/recommend/Accra
    curl http://localhost:5000/recommend/Tamale
"""

try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Run: pip install flask")
    print("Or use the CLI version: python prototype_main.py")

from prototype_main import SimpleInventoryRecommender
import json

if FLASK_AVAILABLE:
    app = Flask(__name__)
    recommender = SimpleInventoryRecommender()

    @app.route('/')
    def home():
        """API documentation."""
        return jsonify({
            'service': 'Kola Market Basic Prototype API',
            'version': '1.0',
            'endpoints': {
                'GET /recommend/{location}': 'Get recommendations for Accra or Tamale',
                'GET /health': 'Service health check'
            },
            'example': 'curl http://localhost:5000/recommend/Accra'
        })

    @app.route('/recommend/<location>')
    def get_recommendations(location):
        """Get recommendations for a location."""
        if location not in ['Accra', 'Tamale']:
            return jsonify({
                'error': f'Invalid location: {location}',
                'valid_locations': ['Accra', 'Tamale']
            }), 400
        
        try:
            # Get JSON format recommendations
            result = recommender.export_json(location)
            return jsonify(result)
        
        except Exception as e:
            return jsonify({
                'error': 'Failed to generate recommendations',
                'message': str(e)
            }), 500

    @app.route('/health')
    def health():
        """Simple health check."""
        try:
            # Test the recommender
            test = recommender.get_recommendations('Accra')
            return jsonify({
                'status': 'healthy',
                'service': 'Kola Market Prototype',
                'test_passed': len(test) > 100  # Basic test
            })
        except:
            return jsonify({'status': 'unhealthy'}), 500

    @app.route('/whatsapp', methods=['POST'])
    def whatsapp_integration():
        """Sample WhatsApp bot integration endpoint."""
        try:
            data = request.json or {}
            message = data.get('message', '').lower()
            
            # Simple location detection
            if 'accra' in message:
                location = 'Accra'
            elif 'tamale' in message:
                location = 'Tamale'
            else:
                return jsonify({
                    'response': 'Hi! I can help with inventory for Accra or Tamale. Which location?'
                })
            
            # Get recommendations
            recommendations = recommender.get_recommendations(location)
            
            # Format for WhatsApp (simplified)
            response = f"📍 *{location} Inventory Tips:*\n\n"
            lines = recommendations.split('\n')
            key_lines = [line for line in lines if ('peak' in line.lower() or 'maintain' in line.lower())]
            
            for line in key_lines[:3]:  # Top 3 insights
                if line.strip():
                    response += f"• {line.strip()}\n"
            
            response += "\nNeed more details? Just ask! 📊"
            
            return jsonify({'response': response})
            
        except Exception as e:
            return jsonify({'response': 'Sorry, something went wrong. Try again!'})

if __name__ == '__main__':
    if not FLASK_AVAILABLE:
        print("Install Flask to run API: pip install flask")
        print("Or use CLI: python prototype_main.py Accra")
        exit(1)
    
    print("🇬🇭 Kola Market Prototype API Starting...")
    print("Available at: http://localhost:5000")
    print()
    print("Test endpoints:")
    print("• http://localhost:5000/recommend/Accra")
    print("• http://localhost:5000/recommend/Tamale") 
    print("• http://localhost:5000/health")
    print()
    print("Integration ready for:")
    print("✓ WhatsApp bots (/whatsapp endpoint)")
    print("✓ Mobile apps (JSON API)")
    print("✓ Dashboards (structured data)")
    
    app.run(host='0.0.0.0', port=5000, debug=True)