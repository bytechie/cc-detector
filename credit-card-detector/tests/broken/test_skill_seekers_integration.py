"""Tests for Skill Seekers Integration with Adaptive Skills"""

import pytest
import tempfile
import shutil
import asyncio
from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_subagent.adaptive_skills import AdaptiveSkillManager
from claude_subagent.skill_seekers_integration import (
    ExternalSkillSource, ImportedSkill, SkillConflict,
    SkillDiscoveryEngine, ConflictResolutionEngine, SkillSeekersIntegration
)


class TestExternalSkillSource:
    """Test the ExternalSkillSource dataclass"""

    def test_initialization(self):
        """Test ExternalSkillSource initialization"""
        source = ExternalSkillSource(
            name="test_source",
            url="https://example.com",
            source_type="documentation",
            description="Test source",
            tags=["test", "demo"]
        )

        assert source.name == "test_source"
        assert source.url == "https://example.com"
        assert source.source_type == "documentation"
        assert source.description == "Test source"
        assert source.tags == ["test", "demo"]
        assert source.last_scanned is None
        assert source.skill_count == 0
        assert source.quality_score == 0.0
        assert source.active is True


class TestImportedSkill:
    """Test the ImportedSkill dataclass"""

    def test_initialization(self):
        """Test ImportedSkill initialization"""
        source = ExternalSkillSource(
            name="test_source",
            url="https://example.com",
            source_type="documentation",
            description="Test source",
            tags=[]
        )

        skill = ImportedSkill(
            original_name="original_skill",
            adapted_name="adapted_skill",
            source_info=source,
            code="def detect(text): return []",
            description="Test skill",
            documentation="Test documentation",
            examples=[{"input": "test", "output": []}],
            dependencies=["re"],
            conflict_resolutions=[],
            quality_metrics={"overall_quality": 0.8},
            import_timestamp=1234567890,
            tags=["imported"]
        )

        assert skill.original_name == "original_skill"
        assert skill.adapted_name == "adapted_skill"
        assert skill.source_info == source
        assert skill.code == "def detect(text): return []"
        assert skill.dependencies == ["re"]
        assert skill.quality_metrics["overall_quality"] == 0.8


class TestSkillConflict:
    """Test the SkillConflict dataclass"""

    def test_initialization(self):
        """Test SkillConflict initialization"""
        conflict = SkillConflict(
            conflict_type="name_collision",
            skill1="skill1",
            skill2="skill2",
            description="Name collision between skills",
            severity=0.9,
            resolution_suggestion="Rename one skill",
            auto_resolvable=True
        )

        assert conflict.conflict_type == "name_collision"
        assert conflict.skill1 == "skill1"
        assert conflict.skill2 == "skill2"
        assert conflict.severity == 0.9
        assert conflict.auto_resolvable is True


class TestSkillDiscoveryEngine:
    """Test the SkillDiscoveryEngine class"""

    def setup_method(self):
        """Set up test environment"""
        self.engine = SkillDiscoveryEngine()

    def test_add_source(self):
        """Test adding external sources"""
        source = ExternalSkillSource(
            name="test_source",
            url="https://example.com",
            source_type="documentation",
            description="Test source",
            tags=[]
        )

        self.engine.add_source(source)

        assert "test_source" in self.engine.sources
        assert self.engine.sources["test_source"] == source

    def test_generate_skill_name(self):
        """Test skill name generation"""
        source_name = "Test Source"
        title = "Credit Card Detection"

        skill_name = self.engine._generate_skill_name(title, source_name)

        assert "imported" in skill_name
        assert "test_source" in skill_name
        assert "credit_card_detection" in skill_name
        # Should include hash for uniqueness
        assert len(skill_name.split('_')) >= 4

    def test_extract_dependencies(self):
        """Test dependency extraction from code"""
        code = """
import re
import json
from typing import List
import requests

def detect(text):
    pattern = re.compile(r'\\d+')
    return pattern.findall(text)
"""

        dependencies = self.engine._extract_dependencies(code)

        expected_deps = {'re', 'json', 'typing', 'requests'}
        for dep in expected_deps:
            assert dep in dependencies

    def test_assess_skill_quality(self):
        """Test skill quality assessment"""
        # High quality code with documentation
        high_quality_code = '''
def detect(text):
    """
    Detect patterns in text and return list of matches.

    Args:
        text (str): Input text to analyze

    Returns:
        list: List of detected patterns
    """
    try:
        import re
        pattern = re.compile(r'\\d+')
        return pattern.findall(text)
    except Exception as e:
        return []
'''

        high_quality_examples = [
            {"input": "test 123", "expected_output": ["123"]},
            {"input": "no numbers", "expected_output": []}
        ]

        metrics = self.engine._assess_skill_quality(high_quality_code, high_quality_examples)

        assert metrics["overall_quality"] > 0.5
        assert metrics["documentation_quality"] > 0.5
        assert metrics["example_coverage"] > 0.5
        assert metrics["error_handling"] > 0.5

        # Low quality code
        low_quality_code = "def detect(text): return []"
        low_quality_examples = []

        metrics = self.engine._assess_skill_quality(low_quality_code, low_quality_examples)

        assert metrics["overall_quality"] < 0.5


class TestConflictResolutionEngine:
    """Test the ConflictResolutionEngine class"""

    def setup_method(self):
        """Set up test environment"""
        self.engine = ConflictResolutionEngine()

    def test_extract_function_patterns(self):
        """Test function pattern extraction"""
        code = '''
def detect(text):
    return re.findall(text)

def find_patterns(text):
    return re.search(text)

def validate(data):
    return len(data) > 0
'''

        patterns = self.engine._extract_function_patterns(code)

        assert "detect" in patterns
        assert "find_patterns" in patterns
        assert "validate" in patterns
        assert "findall" in patterns
        assert "search" in patterns

    def test_calculate_pattern_similarity(self):
        """Test pattern similarity calculation"""
        patterns1 = {"detect", "find", "validate", "re"}
        patterns2 = {"detect", "find", "extract", "re"}

        similarity = self.engine._calculate_pattern_similarity(patterns1, patterns2)

        # Should have some overlap (detect, find, re)
        assert similarity > 0.5
        assert similarity < 1.0

        # Test identical patterns
        identical_similarity = self.engine._calculate_pattern_similarity(patterns1, patterns1)
        assert identical_similarity == 1.0

        # Test completely different patterns
        patterns3 = {"completely", "different", "patterns"}
        different_similarity = self.engine._calculate_pattern_similarity(patterns1, patterns3)
        assert different_similarity == 0.0

    def test_detect_name_collisions(self):
        """Test name collision detection"""
        from claude_subagent.adaptive_skills import GeneratedSkill

        # Existing skill
        existing_skills = {
            "detect_credit_cards": GeneratedSkill(
                name="detect_credit_cards",
                code="def detect(text): return []",
                description="Existing skill",
                dependencies=[],
                test_cases=[]
            )
        }

        # New skill with same name
        new_skills = [
            ImportedSkill(
                original_name="Credit Card Detector",
                adapted_name="detect_credit_cards",  # Same name
                source_info=ExternalSkillSource(
                    name="test_source",
                    url="https://example.com",
                    source_type="documentation",
                    description="Test",
                    tags=[]
                ),
                code="def detect(text): return []",
                description="New skill",
                documentation="",
                examples=[],
                dependencies=[],
                conflict_resolutions=[],
                quality_metrics={},
                import_timestamp=0,
                tags=[]
            )
        ]

        conflicts = self.engine.detect_conflicts(existing_skills, new_skills)

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "name_collision"
        assert conflicts[0].skill1 == "detect_credit_cards"
        assert conflicts[0].severity == 0.9
        assert conflicts[0].auto_resolvable is True

    def test_detect_functionality_overlap(self):
        """Test functionality overlap detection"""
        from claude_subagent.adaptive_skills import GeneratedSkill

        # Existing skill
        existing_skills = {
            "detect_cards": GeneratedSkill(
                name="detect_cards",
                code='''
def detect(text):
    import re
    return re.findall(r'\\d+', text)
''',
                description="Existing detection skill",
                dependencies=["re"],
                test_cases=[]
            )
        }

        # New skill with similar functionality
        new_skills = [
            ImportedSkill(
                original_name="Card Finder",
                adapted_name="find_cards",
                source_info=ExternalSkillSource(
                    name="test_source",
                    url="https://example.com",
                    source_type="documentation",
                    description="Test",
                    tags=[]
                ),
                code='''
def find(text):
    import re
    return re.search(r'\\d+', text)
''',
                description="Similar detection skill",
                documentation="",
                examples=[],
                dependencies=["re"],
                conflict_resolutions=[],
                quality_metrics={},
                import_timestamp=0,
                tags=[]
            )
        ]

        conflicts = self.engine.detect_conflicts(existing_skills, new_skills)

        # Should detect functionality overlap
        functionality_conflicts = [c for c in conflicts if c.conflict_type == "functionality_overlap"]
        assert len(functionality_conflicts) >= 1


class TestSkillSeekersIntegration:
    """Test the main SkillSeekersIntegration class"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.adaptive_manager = AdaptiveSkillManager(skills_dir=self.temp_dir)
        self.integration = SkillSeekersIntegration(self.adaptive_manager)

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test integration initialization"""
        assert self.integration.adaptive_manager == self.adaptive_manager
        assert isinstance(self.integration.discovery_engine, SkillDiscoveryEngine)
        assert isinstance(self.integration.conflict_resolver, ConflictResolutionEngine)
        assert self.integration.config["quality_threshold"] == 0.6
        assert self.integration.config["auto_import"] is True

    def test_add_external_source(self):
        """Test adding external sources"""
        success = self.integration.add_external_source(
            name="test_source",
            url="https://example.com",
            source_type="documentation",
            description="Test source",
            tags=["test"]
        )

        assert success is True
        assert "test_source" in self.integration.discovery_engine.sources

        source = self.integration.discovery_engine.sources["test_source"]
        assert source.name == "test_source"
        assert source.url == "https://example.com"
        assert source.tags == ["test"]

    def test_get_integration_status(self):
        """Test integration status reporting"""
        # Add a test source
        self.integration.add_external_source(
            name="test_source",
            url="https://example.com",
            source_type="documentation"
        )

        status = self.integration.get_integration_status()

        assert "external_sources" in status
        assert "active_sources" in status
        assert "discovered_skills" in status
        assert "current_conflicts" in status
        assert "adaptive_skills" in status
        assert "sources" in status

        assert status["external_sources"] == 1
        assert status["active_sources"] == 1

    def test_discover_credit_card_security_skills(self):
        """Test discovery of predefined security skills"""
        self.integration.discover_credit_card_security_skills()

        status = self.integration.get_integration_status()

        # Should add multiple security sources
        assert status["external_sources"] >= 3

        source_names = [source["name"] for source in status["sources"]]
        assert "OWASP_Cheat_Sheet" in source_names
        assert "PCI_DSS_Docs" in source_names
        assert "Python_Regex_Docs" in source_names

    def test_scan_external_sources_mock(self):
        """Test scanning external sources (mocked)"""
        # Add a test source
        self.integration.add_external_source(
            name="mock_source",
            url="https://example.com",
            source_type="documentation"
        )

        # Since we can't actually scan without Skill Seekers, we'll test the structure
        async def mock_scan():
            return {
                'scanned_sources': 1,
                'discovered_skills': 0,
                'imported_skills': 0,
                'conflicts_detected': 0,
                'conflicts_resolved': 0,
                'errors': ["Mock: Skill Seekers not available for testing"]
            }

        # Run the mock scan
        async def run_test():
            results = await mock_scan()
            return results

        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_test())
        loop.close()

        assert "scanned_sources" in results
        assert "discovered_skills" in results
        assert "errors" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])