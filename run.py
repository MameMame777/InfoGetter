#!/usr/bin/env python3
"""
InfoGatherer Main Execution Script
Academic paper collection and summarization system with Academic LocalLLM
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import InfoGatherer


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="InfoGatherer - Academic Paper Collection and Summarization")
    parser.add_argument("--sources", 
                       help="Comma-separated list of sources to run (xilinx,altera,arxiv)")
    parser.add_argument("--no-email", 
                       action="store_true",
                       help="Disable email notifications")
    parser.add_argument("--config", 
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    print("🚀 Starting InfoGatherer with Academic LocalLLM...")
    
    try:
        # Set config path
        config_path = args.config
        if not config_path:
            config_path = project_root / "config" / "settings.yaml"
        
        # Initialize InfoGatherer
        print("📝 Initializing InfoGatherer...")
        gatherer = InfoGatherer(str(config_path))
        
        # Parse sources
        sources = None
        if args.sources:
            sources = [s.strip() for s in args.sources.split(",")]
            print(f"📚 Running sources: {sources}")
        
        # Set email preference
        send_email = not args.no_email
        if not send_email:
            print("📧 Email notifications disabled")
        
        # Run the gathering process
        print("🔍 Starting data collection and analysis...")
        results = gatherer.run(sources=sources, send_email=send_email)
        
        print(f"\n✅ InfoGatherer completed successfully!")
        print(f"📊 Results summary:")
        for source, documents in results.items():
            print(f"   • {source}: {len(documents)} documents")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ InfoGatherer failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
