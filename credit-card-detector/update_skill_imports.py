#!/usr/bin/env python3
"""
Script to update skill imports after reorganization
"""

import os
import re

def update_imports_in_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Update core skills imports
        content = re.sub(
            r'from claude_subagent\.skills import',
            r'from skills.core import',
            content
        )

        # Update adaptive skills imports
        content = re.sub(
            r'from claude_subagent\.adaptive_skills import',
            r'from skills.adaptive import',
            content
        )

        # Update integration skills imports
        content = re.sub(
            r'from claude_subagent\.skill_seekers_integration import',
            r'from skills.integration.skill_seekers_integration import',
            content
        )

        # Update complex imports with specific modules
        content = re.sub(
            r'from claude_subagent\.skill_seekers_integration\.example_integration import',
            r'from skills.integration.skill_seekers_integration.example_integration import',
            content
        )

        # Update old integration imports to new structure
        content = re.sub(
            r'from skills\.integration\.example_integration import',
            r'from skills.integration.skill_seekers_integration.example_integration import',
            content
        )

        # If content changed, write back to file
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Updated imports in: {file_path}")
            return True
        else:
            print(f"ℹ️  No imports to update in: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all skill imports in the project."""
    # Files that need updating
    files_to_update = [
        'claude_subagent/app_with_metrics.py',
        'claude_subagent/enhanced_adaptive_app.py',
        'claude_subagent/app.py',
        'claude_subagent/adaptive_app.py',
        'claude_subagent/skills/detect_credit_cards_presidio.py',
        'claude_subagent/resource_aware_adaptive_app.py'
    ]

    updated_files = 0

    print("🔄 Updating skill imports after reorganization...")
    print("=" * 50)

    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_imports_in_file(file_path):
                updated_files += 1
        else:
            print(f"⚠️  File not found: {file_path}")

    print("=" * 50)
    print(f"✅ Import update complete! Updated {updated_files} files.")

    # Also update skills/core internal import
    presidio_file = 'skills/core/detect_credit_cards_presidio.py'
    if os.path.exists(presidio_file):
        with open(presidio_file, 'r') as f:
            content = f.read()

        # Update local import within core module
        content = re.sub(
            r'from claude_subagent\.skills import detect_credit_cards as local_detect',
            r'from .detect_credit_cards import detect_credit_cards as local_detect',
            content
        )

        with open(presidio_file, 'w') as f:
            f.write(content)
        print(f"✅ Updated local import in: {presidio_file}")

if __name__ == '__main__':
    main()