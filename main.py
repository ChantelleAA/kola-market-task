"""
Ghana Inventory Recommendation System
Main application entry point

Author: Kola Market Development Team
Version: 2.0.0
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from src.inventory_recommender import GhanaInventoryRecommender
from src.config_manager import ConfigManager
from src.utils.logger import setup_logger


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='Ghana Business Inventory Recommendation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --locations Accra Kumasi
  python main.py --locations Tamale --month 12
  python main.py --locations "Cape Coast" --format json --output results.json
        """
    )
    
    parser.add_argument(
        '--locations', 
        nargs='+',
        help='Locations to analyze (e.g., Accra, Kumasi, Tamale, "Cape Coast")'
    )
    
    parser.add_argument(
        '--month', 
        type=int, 
        choices=range(1, 13),
        help='Target month (1-12, default: current month)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='data/ghana_market_data.json',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--recommendations',
        type=int,
        default=5,
        help='Number of recommendations to show (default: 5)'
    )
    
    parser.add_argument(
        '--format',
        choices=['console', 'json', 'csv'],
        default='console',
        help='Output format (default: console)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (for json/csv formats)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('ghana_inventory', args.log_level)
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        
        config_manager = ConfigManager(config_path)
        
        # Initialize recommender
        recommender = GhanaInventoryRecommender(config_manager)
        
        # Determine locations to analyze
        if args.locations:
            locations = args.locations
        else:
            # Default to available locations
            locations = list(config_manager.get_regions().keys())
            logger.info(f"No locations specified, using all available: {locations}")
        
        # Validate locations
        available_locations = list(config_manager.get_regions().keys())
        invalid_locations = [loc for loc in locations if loc not in available_locations]
        
        if invalid_locations:
            logger.error(f"Invalid locations: {invalid_locations}")
            logger.info(f"Available locations: {available_locations}")
            sys.exit(1)
        
        # Get recommendations for each location
        target_month = args.month or datetime.now().month
        all_results = {}
        
        for location in locations:
            logger.info(f"Generating recommendations for {location}")
            recommendations = recommender.get_recommendations(
                location=location,
                num_recommendations=args.recommendations,
                target_month=target_month
            )
            all_results[location] = recommendations
        
        # Output results
        if args.format == 'console':
            recommender.print_recommendations_console(all_results, target_month)
        elif args.format == 'json':
            output_path = args.output or f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            recommender.export_recommendations_json(all_results, output_path, target_month)
            logger.info(f"Results exported to {output_path}")
        elif args.format == 'csv':
            output_path = args.output or f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            recommender.export_recommendations_csv(all_results, output_path, target_month)
            logger.info(f"Results exported to {output_path}")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        if args.log_level == 'DEBUG':
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()