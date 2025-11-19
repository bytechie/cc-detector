"""
Main entry point for Skill Seekers Integration

This module provides the main function for the Skill Seekers Integration
without causing circular imports.
"""

import asyncio
import sys
from pathlib import Path

def main():
    """Main entry point for Skill Seekers Integration examples"""
    print("🚀 Skill Seekers Integration - Main Entry Point")
    print("=" * 50)

    # Check if dependencies are available
    try:
        # Add parent directories to path for imports
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

        from skills.integration.skill_seekers_integration import SKILL_SEEKERS_AVAILABLE

        if not SKILL_SEEKERS_AVAILABLE:
            print("❌ Skill Seekers Integration is not available")
            print("This may be due to missing dependencies:")
            print("   - skill_seekers package")
            print("   - adaptive skills module")
            return False

        print("✅ Skill Seekers Integration is available!")

        # Run the example if dependencies are met
        try:
            from .example_integration import example_basic_integration
            print("\n🔄 Running basic integration example...")
            asyncio.run(example_basic_integration())
            print("✅ Integration example completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error running integration example: {e}")
            return False

    except Exception as e:
        print(f"❌ Error initializing Skill Seekers Integration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)