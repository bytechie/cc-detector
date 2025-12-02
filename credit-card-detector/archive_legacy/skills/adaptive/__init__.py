"""Adaptive Skill System for Credit Card Detector

This module implements a meta-learning system that can automatically create,
validate, and deploy Claude Skills to adapt to new patterns and requirements.
"""

import ast
import importlib.util
import json
import os
import re
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import requests


@dataclass
class SkillPerformance:
    """Tracks performance metrics for a skill"""
    skill_name: str
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    last_updated: float = 0.0

    def update_metrics(self, tp: int = 0, fp: int = 0, fn: int = 0):
        """Update performance metrics"""
        self.true_positives += tp
        self.false_positives += fp
        self.false_negatives += fn

        # Calculate derived metrics
        total_predicted = self.true_positives + self.false_positives
        total_actual = self.true_positives + self.false_negatives

        if total_predicted > 0:
            self.precision = self.true_positives / total_predicted
        if total_actual > 0:
            self.recall = self.true_positives / total_actual

        if self.precision + self.recall > 0:
            self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)

        self.last_updated = time.time()


@dataclass
class SkillGap:
    """Represents a gap in current skill capabilities"""
    pattern: str
    description: str
    examples: List[str]
    expected_output: List[Any]
    severity: float  # 0.0 to 1.0
    frequency: int = 1


@dataclass
class GeneratedSkill:
    """Represents a newly generated skill"""
    name: str
    code: str
    description: str
    dependencies: List[str]
    test_cases: List[Dict[str, Any]]
    performance: Optional[SkillPerformance] = None


class SkillTemplate(ABC):
    """Abstract base class for skill templates"""

    @abstractmethod
    def generate_code(self, parameters: Dict[str, Any]) -> str:
        """Generate skill code based on parameters"""
        pass

    @abstractmethod
    def get_test_cases(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for the skill"""
        pass


class CreditCardDetectionTemplate(SkillTemplate):
    """Template for credit card detection skills"""

    def generate_code(self, parameters: Dict[str, Any]) -> str:
        """Generate credit card detection skill code"""
        pattern = parameters.get('pattern', r'(?:\d[ -]?){13,19}\d')
        description = parameters.get('description', 'Generated credit card detection')

        return f'''"""
{description}

Auto-generated credit card detection skill.
Generated at: {time.ctime()}
"""

import re

_PATTERN = re.compile(r'{pattern}')

def _luhn(number: str) -> bool:
    """Luhn algorithm validation"""
    if not number.isdigit():
        return False
    digits = [int(d) for d in number]
    total = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        if i % 2 == 1:
            dbl = d * 2
            if dbl > 9:
                dbl -= 9
            total += dbl
        else:
            total += d
    return total % 10 == 0

def detect(text: str):
    """Detect credit card numbers in text"""
    results = []
    for m in _PATTERN.finditer(text):
        raw = m.group(0)
        digits = re.sub(r"\\D", "", raw)
        if not (13 <= len(digits) <= 19):
            continue
        valid = _luhn(digits)
        results.append({{
            "start": m.start(),
            "end": m.end(),
            "raw": raw,
            "number": digits,
            "valid": valid,
        }})
    return results
'''

    def get_test_cases(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for credit card detection"""
        return [
            {
                "input": "Visa: 4111 1111 1111 1111",
                "expected_count": 1,
                "expected_valid": True
            },
            {
                "input": "Invalid: 1234 5678 9012 3456",
                "expected_count": 1,
                "expected_valid": False
            },
            {
                "input": "No cards here",
                "expected_count": 0
            }
        ]


class LLMSkillGenerator:
    """Uses Claude to generate skills for complex patterns"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.endpoint = os.getenv('CLAUDE_API_ENDPOINT', 'https://api.anthropic.com/v1/messages')

    def generate_skill(self, gap: SkillGap, context: Dict[str, Any]) -> Optional[GeneratedSkill]:
        """Generate a skill using Claude LLM"""
        if not self.api_key:
            print("Warning: No Claude API key found, skipping LLM generation")
            return None

        prompt = self._build_prompt(gap, context)

        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key
                },
                json={
                    "model": "claude-3-sonnet-20241022",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            if response.status_code == 200:
                result = response.json()
                skill_code = result['content'][0]['text']
                return self._parse_llm_response(skill_code, gap)
            else:
                print(f"LLM API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error generating skill with LLM: {e}")
            return None

    def _build_prompt(self, gap: SkillGap, context: Dict[str, Any]) -> str:
        """Build prompt for LLM skill generation"""
        return f"""You are an expert Python developer specializing in pattern detection and data security.

TASK: Generate a Python skill to detect the following pattern:
- Pattern: {gap.pattern}
- Description: {gap.description}
- Examples: {json.dumps(gap.examples, indent=2)}

CONTEXT:
This skill will be integrated into a credit card detection system. It should follow this interface:

```python
def detect(text: str):
    \"\"\"
    Detect patterns in text and return list of detections.
    Each detection should be a dict with: start, end, raw, and any additional fields.
    \"\"\"
    results = []
    # Your detection logic here
    return results
```

REQUIREMENTS:
1. Return a list of detection dictionaries
2. Each detection must include 'start', 'end', and 'raw' keys
3. Use regex for pattern matching where appropriate
4. Include validation logic if relevant (like Luhn for credit cards)
5. Add comprehensive docstring
6. Include error handling
7. Make the code production-ready with proper logging

Please generate only the complete Python code for the skill, wrapped in a single code block.
"""

    def _parse_llm_response(self, response: str, gap: SkillGap) -> Optional[GeneratedSkill]:
        """Parse LLM response into GeneratedSkill"""
        try:
            # Extract code block
            code_match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
            if not code_match:
                return None

            code = code_match.group(1)

            # Validate that the code has the required structure
            if not self._validate_skill_code(code):
                return None

            # Extract skill name from the code or generate one
            skill_name = self._extract_skill_name(code) or f"detect_{hash(gap.pattern) % 10000}"

            return GeneratedSkill(
                name=skill_name,
                code=code,
                description=f"Auto-generated skill for: {gap.description}",
                dependencies=["re"],
                test_cases=self._generate_test_cases_from_examples(gap.examples)
            )

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return None

    def _validate_skill_code(self, code: str) -> bool:
        """Validate that skill code meets requirements"""
        try:
            tree = ast.parse(code)
            # Check for detect function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'detect':
                    return True
            return False
        except:
            return False

    def _extract_skill_name(self, code: str) -> Optional[str]:
        """Extract skill name from code"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'detect':
                    # Look for module-level constants or variables that might indicate name
                    pass
            return None
        except:
            return None

    def _generate_test_cases_from_examples(self, examples: List[str]) -> List[Dict[str, Any]]:
        """Generate test cases from example inputs"""
        test_cases = []
        for example in examples:
            test_cases.append({
                "input": example,
                "expected_min_count": 1  # At least one detection expected
            })
        return test_cases


class AdaptiveSkillManager:
    """Main orchestrator for adaptive skill management"""

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(exist_ok=True)

        self.skill_registry: Dict[str, GeneratedSkill] = {}
        self.performance_metrics: Dict[str, SkillPerformance] = {}
        self.templates = {
            "credit_card_detection": CreditCardDetectionTemplate()
        }
        self.llm_generator = LLMSkillGenerator()

        # Load existing skills
        self._load_existing_skills()

    def analyze_and_adapt(self, test_data: List[Dict[str, Any]],
                         expected_outputs: List[List[Dict[str, Any]]]) -> List[GeneratedSkill]:
        """Analyze performance and generate new skills to fill gaps"""
        gaps = self.identify_skill_gaps(test_data, expected_outputs)
        new_skills = []

        for gap in gaps:
            skill = self.generate_skill_for_gap(gap)
            if skill:
                if self.test_and_deploy_skill(skill):
                    new_skills.append(skill)

        return new_skills

    def identify_skill_gaps(self, test_data: List[Dict[str, Any]],
                           expected_outputs: List[List[Dict[str, Any]]]) -> List[SkillGap]:
        """Identify patterns where current skills fail"""
        gaps = []

        for i, (test_case, expected) in enumerate(zip(test_data, expected_outputs)):
            input_text = test_case["input"]

            # Test all existing skills
            all_detections = []
            for skill_name, skill in self.skill_registry.items():
                detections = self._execute_skill(skill, input_text)
                all_detections.extend(detections)

            # Compare with expected
            missing_patterns = self._find_missing_patterns(all_detections, expected)

            if missing_patterns:
                gap = SkillGap(
                    pattern=f"gap_{i}",
                    description=f"Missing detection in test case {i}",
                    examples=[input_text],
                    expected_output=expected,
                    severity=len(missing_patterns) / max(len(expected), 1),
                    frequency=1
                )
                gaps.append(gap)

        return gaps

    def generate_skill_for_gap(self, gap: SkillGap) -> Optional[GeneratedSkill]:
        """Generate a skill to address a specific gap"""
        # Try template-based generation first
        if "credit card" in gap.description.lower():
            template = self.templates["credit_card_detection"]
            params = {
                "pattern": gap.pattern,
                "description": gap.description
            }
            code = template.generate_code(params)
            test_cases = template.get_test_cases(params)

            return GeneratedSkill(
                name=f"detect_credit_card_{hash(gap.pattern) % 10000}",
                code=code,
                description=f"Template-based skill for: {gap.description}",
                dependencies=["re"],
                test_cases=test_cases
            )

        # Fall back to LLM generation
        else:
            return self.llm_generator.generate_skill(gap, {"existing_skills": list(self.skill_registry.keys())})

    def test_and_deploy_skill(self, skill: GeneratedSkill) -> bool:
        """Test a skill and deploy it if it passes validation"""
        # Validate syntax
        if not self._validate_skill_syntax(skill.code):
            return False

        # Run test cases
        if not self._run_skill_tests(skill):
            return False

        # Deploy the skill
        skill_file = self.skills_dir / f"{skill.name}.py"
        with open(skill_file, 'w') as f:
            f.write(skill.code)

        # Register the skill
        self.skill_registry[skill.name] = skill
        self.performance_metrics[skill.name] = SkillPerformance(skill_name=skill.name)

        return True

    def _load_existing_skills(self):
        """Load existing skills from the skills directory"""
        for skill_file in self.skills_dir.glob("*.py"):
            if skill_file.name.startswith("__"):
                continue

            skill_name = skill_file.stem
            try:
                with open(skill_file, 'r') as f:
                    code = f.read()

                skill = GeneratedSkill(
                    name=skill_name,
                    code=code,
                    description=f"Loaded skill: {skill_name}",
                    dependencies=[],
                    test_cases=[]
                )

                self.skill_registry[skill_name] = skill
                self.performance_metrics[skill_name] = SkillPerformance(skill_name=skill_name)

            except Exception as e:
                print(f"Error loading skill {skill_name}: {e}")

    def _execute_skill(self, skill: GeneratedSkill, text: str) -> List[Dict[str, Any]]:
        """Execute a skill on input text"""
        try:
            # Create a temporary module
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(skill.code)
                temp_file = f.name

            try:
                spec = importlib.util.spec_from_file_location("temp_skill", temp_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'detect'):
                    return module.detect(text)
                else:
                    return []

            finally:
                os.unlink(temp_file)

        except Exception as e:
            print(f"Error executing skill {skill.name}: {e}")
            return []

    def _validate_skill_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _run_skill_tests(self, skill: GeneratedSkill) -> bool:
        """Run test cases for a skill"""
        for test_case in skill.test_cases:
            try:
                result = self._execute_skill(skill, test_case["input"])

                # Basic validation
                if "expected_count" in test_case:
                    if len(result) != test_case["expected_count"]:
                        return False

                if "expected_min_count" in test_case:
                    if len(result) < test_case["expected_min_count"]:
                        return False

            except Exception as e:
                print(f"Test failed for skill {skill.name}: {e}")
                return False

        return True

    def _find_missing_patterns(self, actual: List[Dict[str, Any]],
                              expected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find patterns that are missing from actual results"""
        missing = []

        for exp_item in expected:
            found = False
            exp_text = exp_item.get('raw', '')

            for act_item in actual:
                act_text = act_item.get('raw', '')
                if exp_text in act_text or act_text in exp_text:
                    found = True
                    break

            if not found:
                missing.append(exp_item)

        return missing

    def get_skill_performance(self, skill_name: str) -> Optional[SkillPerformance]:
        """Get performance metrics for a skill"""
        return self.performance_metrics.get(skill_name)

    def update_skill_performance(self, skill_name: str, tp: int = 0, fp: int = 0, fn: int = 0):
        """Update performance metrics for a skill"""
        if skill_name in self.performance_metrics:
            self.performance_metrics[skill_name].update_metrics(tp, fp, fn)

    def list_skills(self) -> List[str]:
        """List all registered skills"""
        return list(self.skill_registry.keys())

    def get_best_skill_for_pattern(self, pattern_description: str) -> Optional[str]:
        """Get the best performing skill for a given pattern"""
        best_skill = None
        best_score = -1

        for skill_name, perf in self.performance_metrics.items():
            if perf.f1_score > best_score:
                best_score = perf.f1_score
                best_skill = skill_name

        return best_skill