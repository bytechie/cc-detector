"""Tests for the Adaptive Skill System"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the adaptive skills
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_subagent.adaptive_skills import (
    AdaptiveSkillManager, SkillGap, GeneratedSkill, SkillPerformance,
    CreditCardDetectionTemplate, LLMSkillGenerator
)


class TestSkillPerformance:
    """Test the SkillPerformance class"""

    def test_initialization(self):
        """Test SkillPerformance initialization"""
        perf = SkillPerformance(skill_name="test_skill")
        assert perf.skill_name == "test_skill"
        assert perf.true_positives == 0
        assert perf.false_positives == 0
        assert perf.false_negatives == 0
        assert perf.accuracy == 0.0
        assert perf.precision == 0.0
        assert perf.recall == 0.0
        assert perf.f1_score == 0.0

    def test_update_metrics(self):
        """Test metric updates"""
        perf = SkillPerformance(skill_name="test_skill")

        # Update with some values
        perf.update_metrics(tp=10, fp=2, fn=3)

        assert perf.true_positives == 10
        assert perf.false_positives == 2
        assert perf.false_negatives == 3

        # Check calculated metrics
        expected_precision = 10 / (10 + 2)  # 10/12 = 0.833
        expected_recall = 10 / (10 + 3)     # 10/13 = 0.769
        expected_f1 = 2 * (expected_precision * expected_recall) / (expected_precision + expected_recall)

        assert abs(perf.precision - expected_precision) < 0.001
        assert abs(perf.recall - expected_recall) < 0.001
        assert abs(perf.f1_score - expected_f1) < 0.001


class TestSkillGap:
    """Test the SkillGap class"""

    def test_initialization(self):
        """Test SkillGap initialization"""
        gap = SkillGap(
            pattern="test_pattern",
            description="Test gap",
            examples=["example1", "example2"],
            expected_output=[{"field": "value"}],
            severity=0.5,
            frequency=2
        )

        assert gap.pattern == "test_pattern"
        assert gap.description == "Test gap"
        assert gap.examples == ["example1", "example2"]
        assert gap.expected_output == [{"field": "value"}]
        assert gap.severity == 0.5
        assert gap.frequency == 2


class TestGeneratedSkill:
    """Test the GeneratedSkill class"""

    def test_initialization(self):
        """Test GeneratedSkill initialization"""
        skill = GeneratedSkill(
            name="test_skill",
            code="def detect(text): return []",
            description="Test skill",
            dependencies=["re"],
            test_cases=[{"input": "test", "expected_count": 0}]
        )

        assert skill.name == "test_skill"
        assert skill.code == "def detect(text): return []"
        assert skill.description == "Test skill"
        assert skill.dependencies == ["re"]
        assert skill.test_cases == [{"input": "test", "expected_count": 0}]
        assert skill.performance is None


class TestCreditCardDetectionTemplate:
    """Test the CreditCardDetectionTemplate class"""

    def test_generate_code(self):
        """Test code generation"""
        template = CreditCardDetectionTemplate()

        parameters = {
            "pattern": r"\\d{4}-\\d{4}-\\d{4}-\\d{4}",
            "description": "Hyphen-separated credit card detection"
        }

        code = template.generate_code(parameters)

        # Check that the code contains expected elements
        assert "def detect(text):" in code
        assert "Hyphen-separated credit card detection" in code
        assert parameters["pattern"] in code
        assert "_luhn" in code

    def test_get_test_cases(self):
        """Test test case generation"""
        template = CreditCardDetectionTemplate()

        test_cases = template.get_test_cases({})

        assert len(test_cases) == 3
        assert "input" in test_cases[0]
        assert "expected_count" in test_cases[0]
        assert test_cases[0]["input"] == "Visa: 4111 1111 1111 1111"


class TestAdaptiveSkillManager:
    """Test the AdaptiveSkillManager class"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = AdaptiveSkillManager(skills_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test manager initialization"""
        assert self.manager.skills_dir.exists()
        assert isinstance(self.manager.skill_registry, dict)
        assert isinstance(self.manager.performance_metrics, dict)
        assert isinstance(self.manager.templates, dict)
        assert "credit_card_detection" in self.manager.templates

    def test_validate_skill_syntax(self):
        """Test skill syntax validation"""
        valid_code = """
def detect(text):
    return []
"""

        invalid_code = """
def detect(text)
    return []
"""

        assert self.manager._validate_skill_syntax(valid_code) == True
        assert self.manager._validate_skill_syntax(invalid_code) == False

    def test_run_skill_tests(self):
        """Test skill test execution"""
        # Create a skill with failing test
        skill = GeneratedSkill(
            name="test_skill",
            code="def detect(text): return [{'raw': 'test'}]",
            description="Test skill",
            dependencies=[],
            test_cases=[
                {"input": "test", "expected_count": 0}  # This will fail
            ]
        )

        # Should fail because test expects 0 but returns 1
        assert self.manager._run_skill_tests(skill) == False

        # Create a skill with passing test
        skill_pass = GeneratedSkill(
            name="test_skill_pass",
            code="def detect(text): return []",
            description="Test skill",
            dependencies=[],
            test_cases=[
                {"input": "test", "expected_count": 0}  # This will pass
            ]
        )

        assert self.manager._run_skill_tests(skill_pass) == True

    def test_test_and_deploy_skill(self):
        """Test skill deployment"""
        skill = GeneratedSkill(
            name="deploy_test",
            code="def detect(text): return []",
            description="Test deployment",
            dependencies=[],
            test_cases=[
                {"input": "test", "expected_count": 0}
            ]
        )

        # Should deploy successfully
        result = self.manager.test_and_deploy_skill(skill)
        assert result == True
        assert skill.name in self.manager.skill_registry
        assert skill.name in self.manager.performance_metrics

    def test_find_missing_patterns(self):
        """Test missing pattern detection"""
        actual = [
            {"raw": "4111111111111111", "start": 0, "end": 16}
        ]

        expected = [
            {"raw": "4111111111111111", "start": 0, "end": 16},
            {"raw": "4242424242424242", "start": 20, "end": 36}  # This one is missing
        ]

        missing = self.manager._find_missing_patterns(actual, expected)
        assert len(missing) == 1
        assert missing[0]["raw"] == "4242424242424242"

    def test_list_skills(self):
        """Test skill listing"""
        # Initially should be empty
        skills = self.manager.list_skills()
        assert isinstance(skills, list)

        # Add a skill
        skill = GeneratedSkill(
            name="list_test",
            code="def detect(text): return []",
            description="Test listing",
            dependencies=[],
            test_cases=[{"input": "test", "expected_count": 0}]
        )

        self.manager.test_and_deploy_skill(skill)

        # Should now contain the skill
        skills = self.manager.list_skills()
        assert "list_test" in skills

    def test_get_skill_performance(self):
        """Test skill performance retrieval"""
        skill_name = "perf_test"

        # Should return None for non-existent skill
        perf = self.manager.get_skill_performance(skill_name)
        assert perf is None

        # Add a skill
        skill = GeneratedSkill(
            name=skill_name,
            code="def detect(text): return []",
            description="Performance test",
            dependencies=[],
            test_cases=[{"input": "test", "expected_count": 0}]
        )

        self.manager.test_and_deploy_skill(skill)

        # Should now return performance object
        perf = self.manager.get_skill_performance(skill_name)
        assert perf is not None
        assert perf.skill_name == skill_name

    def test_update_skill_performance(self):
        """Test skill performance updates"""
        skill_name = "update_test"

        # Add a skill first
        skill = GeneratedSkill(
            name=skill_name,
            code="def detect(text): return []",
            description="Update test",
            dependencies=[],
            test_cases=[{"input": "test", "expected_count": 0}]
        )

        self.manager.test_and_deploy_skill(skill)

        # Update performance
        self.manager.update_skill_performance(skill_name, tp=5, fp=1, fn=2)

        perf = self.manager.get_skill_performance(skill_name)
        assert perf.true_positives == 5
        assert perf.false_positives == 1
        assert perf.false_negatives == 2
        assert perf.precision == 5 / (5 + 1)  # 5/6
        assert perf.recall == 5 / (5 + 2)     # 5/7

    def test_generate_skill_for_gap_credit_card(self):
        """Test skill generation for credit card gaps"""
        gap = SkillGap(
            pattern="credit_card_gap",
            description="Credit card detection gap",
            examples=["4242-4242-4242-4242"],
            expected_output=[{"raw": "4242-4242-4242-4242"}],
            severity=0.8
        )

        skill = self.manager.generate_skill_for_gap(gap)

        assert skill is not None
        assert "credit_card" in skill.name
        assert "def detect(text):" in skill.code
        assert len(skill.test_cases) > 0

    def test_identify_skill_gaps(self):
        """Test gap identification"""
        # Add a basic skill first
        skill = GeneratedSkill(
            name="basic_test",
            code="""
def detect(text):
    # Only detects one specific pattern
    if "4111111111111111" in text:
        return [{"raw": "4111111111111111", "start": 0, "end": 16}]
    return []
""",
            description="Basic test skill",
            dependencies=[],
            test_cases=[]
        )

        self.manager.test_and_deploy_skill(skill)

        # Test data that should reveal gaps
        test_data = [
            {"input": "Card: 4111111111111111"},  # This will be detected
            {"input": "Card: 4242424242424242"},  # This won't be detected (gap)
        ]

        expected_outputs = [
            [{"raw": "4111111111111111", "start": 6, "end": 22}],
            [{"raw": "4242424242424242", "start": 6, "end": 22}],
        ]

        gaps = self.manager.identify_skill_gaps(test_data, expected_outputs)

        # Should identify a gap for the second test case
        assert len(gaps) >= 1
        assert any("4242424242424242" in gap.examples[0] for gap in gaps)


class TestLLMSkillGenerator:
    """Test the LLMSkillGenerator class"""

    def test_initialization(self):
        """Test LLM generator initialization"""
        # Without API key
        generator = LLMSkillGenerator()
        assert generator.api_key is None

        # With mock API key
        generator = LLMSkillGenerator(api_key="test_key")
        assert generator.api_key == "test_key"

    def test_validate_skill_code(self):
        """Test skill code validation"""
        valid_code = """
def detect(text):
    return [{"raw": "test", "start": 0, "end": 4}]
"""

        invalid_code = """
def not_detect(text):
    return "wrong format"
"""

        generator = LLMSkillGenerator()

        assert generator._validate_skill_code(valid_code) == True
        assert generator._validate_skill_code(invalid_code) == False

    def test_generate_test_cases_from_examples(self):
        """Test test case generation from examples"""
        examples = ["4242424242424242", "test input with card"]

        generator = LLMSkillGenerator()
        test_cases = generator._generate_test_cases_from_examples(examples)

        assert len(test_cases) == 2
        assert all("input" in case for case in test_cases)
        assert all(case["input"] in examples for case in test_cases)
        assert all("expected_min_count" in case for case in test_cases)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])