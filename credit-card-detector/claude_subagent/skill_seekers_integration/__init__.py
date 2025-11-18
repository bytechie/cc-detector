"""
Skill Seekers Integration for Adaptive Skills System

This module integrates Skill Seekers capabilities with the adaptive skills framework
to create a comprehensive skill discovery, import, and management system.

Key Features:
- Automatic skill discovery from external sources (docs, GitHub, PDFs)
- Conflict detection and resolution between skills
- Quality assessment and enhancement of imported skills
- Intelligent skill categorization and tagging
- Continuous learning from external knowledge sources
"""

import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import ast
import hashlib

try:
    from skill_seekers.cli import (
        LlmsTxtDetector, LlmsTxtDownloader, LlmsTxtParser,
        read_reference_files
    )
    SKILL_SEEKERS_AVAILABLE = True
except ImportError:
    SKILL_SEEKERS_AVAILABLE = False

from ..adaptive_skills import (
    AdaptiveSkillManager, GeneratedSkill, SkillPerformance, SkillGap
)


@dataclass
class ExternalSkillSource:
    """Represents an external source of skills"""
    name: str
    url: str
    source_type: str  # 'documentation', 'github', 'pdf', 'llms_txt'
    description: str
    tags: List[str]
    last_scanned: Optional[float] = None
    skill_count: int = 0
    quality_score: float = 0.0
    active: bool = True


@dataclass
class ImportedSkill:
    """Represents a skill imported from external sources"""
    original_name: str
    adapted_name: str
    source_info: ExternalSkillSource
    code: str
    description: str
    documentation: str
    examples: List[Dict[str, Any]]
    dependencies: List[str]
    conflict_resolutions: List[str]
    quality_metrics: Dict[str, float]
    import_timestamp: float
    tags: List[str]


@dataclass
class SkillConflict:
    """Represents a conflict between skills"""
    conflict_type: str  # 'name_collision', 'functionality_overlap', 'dependency_conflict'
    skill1: str
    skill2: str
    description: str
    severity: float  # 0.0 to 1.0
    resolution_suggestion: str
    auto_resolvable: bool


class SkillDiscoveryEngine:
    """Discovers skills from various external sources"""

    def __init__(self):
        self.sources: Dict[str, ExternalSkillSource] = {}
        self.discovered_skills: Dict[str, ImportedSkill] = {}
        self.conflicts: List[SkillConflict] = []

    def add_source(self, source: ExternalSkillSource):
        """Add a new external skill source"""
        self.sources[source.name] = source

    async def discover_from_documentation(self, source: ExternalSkillSource) -> List[ImportedSkill]:
        """Discover skills from documentation using llms.txt"""
        if not SKILL_SEEKERS_AVAILABLE:
            print("Warning: Skill Seekers not available, skipping documentation discovery")
            return []

        skills = []

        try:
            # Detect llms.txt variants
            detector = LlmsTxtDetector(source.url)
            variants = detector.detect_all()

            for variant in variants:
                print(f"Found {variant['variant']} at {variant['url']}")

                # Download content
                downloader = LlmsTxtDownloader(variant['url'])
                content = downloader.download()

                if content:
                    # Parse content
                    parser = LlmsTxtParser(content)
                    pages = parser.parse()

                    # Convert pages to skills
                    for page in pages:
                        skill = self._convert_page_to_skill(page, source, variant['variant'])
                        if skill:
                            skills.append(skill)

        except Exception as e:
            print(f"Error discovering skills from {source.url}: {e}")

        return skills

    def _convert_page_to_skill(self, page: Dict[str, Any], source: ExternalSkillSource, variant: str) -> Optional[ImportedSkill]:
        """Convert a documentation page to a skill"""
        try:
            # Extract potential function definitions
            content = page.get('content', '')
            title = page.get('title', 'Untitled')

            # Look for code samples that might be detection functions
            code_samples = page.get('code_samples', [])
            detection_code = self._extract_detection_code(code_samples)

            if detection_code:
                # Create an adapted skill name
                adapted_name = self._generate_skill_name(title, source.name)

                # Generate examples from content
                examples = self._extract_examples_from_content(content)

                # Assess quality
                quality_metrics = self._assess_skill_quality(detection_code, examples)

                return ImportedSkill(
                    original_name=title,
                    adapted_name=adapted_name,
                    source_info=source,
                    code=detection_code,
                    description=f"Imported from {source.name}: {title}",
                    documentation=content,
                    examples=examples,
                    dependencies=self._extract_dependencies(detection_code),
                    conflict_resolutions=[],
                    quality_metrics=quality_metrics,
                    import_timestamp=datetime.now().timestamp(),
                    tags=['documentation', 'imported'] + source.tags
                )

        except Exception as e:
            print(f"Error converting page to skill: {e}")

        return None

    def _extract_detection_code(self, code_samples: List[str]) -> Optional[str]:
        """Extract detection-related code from code samples"""
        detection_patterns = [
            r'def\s+detect\s*\(',
            r'def\s+find\s*\(',
            r'def\s+identify\s*\(',
            r're\.search\s*\(',
            r're\.findall\s*\(',
            r're\.finditer\s*\(',
        ]

        for sample in code_samples:
            # Check if sample contains detection-like patterns
            if any(re.search(pattern, sample, re.IGNORECASE) for pattern in detection_patterns):
                # Try to extract a complete function
                if 'def ' in sample:
                    # Basic function extraction
                    lines = sample.split('\n')
                    func_lines = []
                    indent_level = None

                    for line in lines:
                        if 'def ' in line:
                            indent_level = len(line) - len(line.lstrip())
                        if func_lines or 'def ' in line:
                            func_lines.append(line)
                            # Stop when we return to same or lower indentation
                            if (func_lines[-1].strip() and
                                len(line) - len(line.lstrip()) <= indent_level and
                                len(func_lines) > 1):
                                break

                    if func_lines:
                        return '\n'.join(func_lines)

        return None

    def _generate_skill_name(self, title: str, source_name: str) -> str:
        """Generate a unique skill name"""
        # Clean and normalize title
        clean_title = re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())
        clean_title = re.sub(r'_+', '_', clean_title).strip('_')

        # Add source prefix
        source_prefix = re.sub(r'[^a-zA-Z0-9]', '_', source_name.lower()).strip('_')[:10]

        # Create hash for uniqueness
        content_hash = hashlib.md5(f"{title}_{source_name}".encode()).hexdigest()[:6]

        return f"imported_{source_prefix}_{clean_title}_{content_hash}"

    def _extract_examples_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract examples from documentation content"""
        examples = []

        # Look for code blocks, lists, or specific patterns that indicate examples
        lines = content.split('\n')
        current_example = []
        in_example = False
        example_type = None

        for line in lines:
            # Detect start of examples
            if any(keyword in line.lower() for keyword in ['example:', 'for example:', 'e.g.', 'sample']):
                in_example = True
                example_type = 'text'
                current_example = [line.strip()]
            elif line.strip().startswith('```'):
                if in_example:
                    examples.append({
                        "type": example_type,
                        "content": '\n'.join(current_example),
                        "input": self._extract_input_from_example(current_example),
                        "expected_output": self._extract_output_from_example(current_example)
                    })
                    in_example = False
                    current_example = []
                else:
                    in_example = True
                    example_type = 'code'
            elif in_example:
                current_example.append(line.strip())

        return examples

    def _extract_input_from_example(self, example_lines: List[str]) -> Optional[str]:
        """Extract input from example lines"""
        # Look for patterns that suggest input
        for line in example_lines:
            if any(keyword in line.lower() for keyword in ['input:', 'text:', 'string:']):
                return line.split(':', 1)[1].strip()
        return None

    def _extract_output_from_example(self, example_lines: List[str]) -> Optional[str]:
        """Extract expected output from example lines"""
        for line in example_lines:
            if any(keyword in line.lower() for keyword in ['output:', 'result:', 'return:']):
                return line.split(':', 1)[1].strip()
        return None

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract dependencies from skill code"""
        dependencies = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
        except:
            pass

        return dependencies

    def _assess_skill_quality(self, code: str, examples: List[Dict[str, Any]]) -> Dict[str, float]:
        """Assess the quality of an imported skill"""
        metrics = {
            'code_complexity': 0.5,
            'documentation_quality': 0.5,
            'example_coverage': 0.0,
            'error_handling': 0.5,
            'test_coverage': 0.0
        }

        # Assess code complexity
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            if functions:
                # Simple complexity based on function count and lines
                metrics['code_complexity'] = min(1.0, len(functions) / 5.0)
        except:
            metrics['code_complexity'] = 0.2

        # Assess documentation quality
        docstring_count = sum(1 for node in ast.walk(ast.parse(code))
                            if isinstance(node, ast.FunctionDef) and ast.get_docstring(node))
        functions_count = len([node for node in ast.walk(ast.parse(code))
                             if isinstance(node, ast.FunctionDef)])

        if functions_count > 0:
            metrics['documentation_quality'] = docstring_count / functions_count

        # Assess example coverage
        if examples:
            metrics['example_coverage'] = min(1.0, len(examples) / 3.0)

        # Check for error handling
        error_handling_patterns = ['try:', 'except', 'raise', 'if not:', 'if len(']
        error_count = sum(1 for pattern in error_handling_patterns if pattern in code)
        metrics['error_handling'] = min(1.0, error_count / len(error_handling_patterns))

        # Overall quality score
        metrics['overall_quality'] = sum(metrics.values()) / len(metrics)

        return metrics


class ConflictResolutionEngine:
    """Detects and resolves conflicts between skills"""

    def __init__(self):
        self.conflict_resolvers = {
            'name_collision': self._resolve_name_collision,
            'functionality_overlap': self._resolve_functionality_overlap,
            'dependency_conflict': self._resolve_dependency_conflict
        }

    def detect_conflicts(self, existing_skills: Dict[str, GeneratedSkill],
                        new_skills: List[ImportedSkill]) -> List[SkillConflict]:
        """Detect conflicts between existing and new skills"""
        conflicts = []

        # Check name collisions
        existing_names = set(existing_skills.keys())
        for new_skill in new_skills:
            if new_skill.adapted_name in existing_names:
                conflicts.append(SkillConflict(
                    conflict_type='name_collision',
                    skill1=new_skill.adapted_name,
                    skill2=new_skill.adapted_name,  # Same name
                    description=f"Name collision: {new_skill.adapted_name}",
                    severity=0.9,
                    resolution_suggestion="Rename new skill with unique suffix",
                    auto_resolvable=True
                ))

        # Check functionality overlap
        conflicts.extend(self._detect_functionality_overlap(existing_skills, new_skills))

        # Check dependency conflicts
        conflicts.extend(self._detect_dependency_conflicts(existing_skills, new_skills))

        return conflicts

    def _detect_functionality_overlap(self, existing_skills: Dict[str, GeneratedSkill],
                                    new_skills: List[ImportedSkill]) -> List[SkillConflict]:
        """Detect overlapping functionality between skills"""
        conflicts = []

        # Simple heuristic: check for similar function names and patterns
        for new_skill in new_skills:
            new_patterns = self._extract_function_patterns(new_skill.code)

            for existing_name, existing_skill in existing_skills.items():
                existing_patterns = self._extract_function_patterns(existing_skill.code)

                # Calculate pattern similarity
                similarity = self._calculate_pattern_similarity(new_patterns, existing_patterns)

                if similarity > 0.7:  # High overlap threshold
                    conflicts.append(SkillConflict(
                        conflict_type='functionality_overlap',
                        skill1=new_skill.adapted_name,
                        skill2=existing_name,
                        description=f"High functionality overlap ({similarity:.2f}) between skills",
                        severity=similarity,
                        resolution_suggestion="Choose skill with higher quality score or merge functionality",
                        auto_resolvable=False
                    ))

        return conflicts

    def _detect_dependency_conflicts(self, existing_skills: Dict[str, GeneratedSkill],
                                   new_skills: List[ImportedSkill]) -> List[SkillConflict]:
        """Detect dependency conflicts between skills"""
        conflicts = []

        # Group skills by dependencies
        dep_groups = {}

        for name, skill in existing_skills.items():
            deps = tuple(sorted(skill.dependencies))
            if deps not in dep_groups:
                dep_groups[deps] = []
            dep_groups[deps].append(name)

        for new_skill in new_skills:
            new_deps = tuple(sorted(new_skill.dependencies))
            if new_deps in dep_groups:
                conflicts.append(SkillConflict(
                    conflict_type='dependency_conflict',
                    skill1=new_skill.adapted_name,
                    skill2=', '.join(dep_groups[new_deps]),
                    description=f"Similar dependencies: {new_deps}",
                    severity=0.3,  # Low severity
                    resolution_suggestion="Consider merging or standardizing dependencies",
                    auto_resolvable=True
                ))

        return conflicts

    def _extract_function_patterns(self, code: str) -> Set[str]:
        """Extract unique patterns from skill code"""
        patterns = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    patterns.add(node.name)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        patterns.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        patterns.add(node.func.attr)
        except:
            # Fallback to regex-based extraction
            func_patterns = re.findall(r'def\s+(\w+)', code)
            call_patterns = re.findall(r'(\w+)\s*\(', code)
            patterns.update(func_patterns + call_patterns)

        return patterns

    def _calculate_pattern_similarity(self, patterns1: Set[str], patterns2: Set[str]) -> float:
        """Calculate similarity between two pattern sets"""
        if not patterns1 and not patterns2:
            return 1.0
        if not patterns1 or not patterns2:
            return 0.0

        intersection = len(patterns1.intersection(patterns2))
        union = len(patterns1.union(patterns2))

        return intersection / union if union > 0 else 0.0

    def _resolve_name_collision(self, conflict: SkillConflict, new_skill: ImportedSkill) -> str:
        """Resolve name collision by renaming"""
        timestamp = int(datetime.now().timestamp())
        suffix = f"_{timestamp}"
        new_skill.adapted_name += suffix
        return f"Renamed to {new_skill.adapted_name}"

    def _resolve_functionality_overlap(self, conflict: SkillConflict,
                                     new_skill: ImportedSkill, existing_skill: GeneratedSkill) -> str:
        """Provide guidance for functionality overlap"""
        new_quality = new_skill.quality_metrics.get('overall_quality', 0.5)

        # Get existing skill quality if available
        existing_quality = 0.5  # Default

        if new_quality > existing_quality:
            return f"Keep new skill (higher quality: {new_quality:.2f} vs {existing_quality:.2f})"
        else:
            return f"Keep existing skill (higher quality: {existing_quality:.2f} vs {new_quality:.2f})"

    def _resolve_dependency_conflict(self, conflict: SkillConflict) -> str:
        """Resolve dependency conflict"""
        return "Dependencies compatible, no action needed"

    def resolve_conflicts(self, conflicts: List[SkillConflict],
                         new_skills: List[ImportedSkill]) -> List[str]:
        """Resolve detected conflicts"""
        resolutions = []

        for conflict in conflicts:
            resolver = self.conflict_resolvers.get(conflict.conflict_type)
            if resolver and conflict.auto_resolvable:
                # Find the relevant new skill
                relevant_skill = next((s for s in new_skills if s.adapted_name == conflict.skill1), None)
                if relevant_skill:
                    resolution = resolver(conflict, relevant_skill)
                    resolutions.append(resolution)

        return resolutions


class SkillSeekersIntegration:
    """Main integration class for Skill Seekers + Adaptive Skills"""

    def __init__(self, adaptive_manager: AdaptiveSkillManager):
        self.adaptive_manager = adaptive_manager
        self.discovery_engine = SkillDiscoveryEngine()
        self.conflict_resolver = ConflictResolutionEngine()

        # Configuration
        self.config = {
            'auto_import': True,
            'quality_threshold': 0.6,
            'max_conflicts': 5,
            'scan_interval_hours': 24
        }

    def add_external_source(self, name: str, url: str, source_type: str,
                           description: str = "", tags: List[str] = None) -> bool:
        """Add an external skill source"""
        source = ExternalSkillSource(
            name=name,
            url=url,
            source_type=source_type,
            description=description,
            tags=tags or []
        )

        self.discovery_engine.add_source(source)
        return True

    async def scan_external_sources(self) -> Dict[str, Any]:
        """Scan all external sources for new skills"""
        results = {
            'scanned_sources': 0,
            'discovered_skills': 0,
            'imported_skills': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'errors': []
        }

        for source_name, source in self.discovery_engine.sources.items():
            if not source.active:
                continue

            try:
                print(f"Scanning source: {source_name}")

                if source.source_type == 'documentation':
                    discovered_skills = await self.discovery_engine.discover_from_documentation(source)
                else:
                    # TODO: Implement other source types
                    discovered_skills = []
                    results['errors'].append(f"Source type {source.source_type} not yet implemented")

                results['discovered_skills'] += len(discovered_skills)

                # Process discovered skills
                imported_count = await self._process_discovered_skills(discovered_skills)
                results['imported_skills'] += imported_count

                results['scanned_sources'] += 1
                source.last_scanned = datetime.now().timestamp()
                source.skill_count = len(discovered_skills)

            except Exception as e:
                error_msg = f"Error scanning {source_name}: {e}"
                results['errors'].append(error_msg)
                print(error_msg)

        return results

    async def _process_discovered_skills(self, discovered_skills: List[ImportedSkill]) -> int:
        """Process and import discovered skills"""
        imported_count = 0

        if not discovered_skills:
            return 0

        # Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(
            self.adaptive_manager.skill_registry,
            discovered_skills
        )

        # Filter skills by quality threshold
        high_quality_skills = [
            skill for skill in discovered_skills
            if skill.quality_metrics.get('overall_quality', 0) >= self.config['quality_threshold']
        ]

        # Resolve conflicts
        if len(conflicts) <= self.config['max_conflicts']:
            resolutions = self.conflict_resolver.resolve_conflicts(conflicts, high_quality_skills)

            # Import skills
            for skill in high_quality_skills:
                if await self._import_skill(skill):
                    imported_count += 1
        else:
            print(f"Too many conflicts ({len(conflicts)}), skipping import")

        return imported_count

    async def _import_skill(self, imported_skill: ImportedSkill) -> bool:
        """Import a single skill into the adaptive manager"""
        try:
            # Convert to GeneratedSkill
            generated_skill = GeneratedSkill(
                name=imported_skill.adapted_name,
                code=imported_skill.code,
                description=imported_skill.description,
                dependencies=imported_skill.dependencies,
                test_cases=imported_skill.examples
            )

            # Test and deploy
            if self.adaptive_manager.test_and_deploy_skill(generated_skill):
                # Store additional metadata
                self.adaptive_manager.skill_registry[imported_skill.adapted_name] = generated_skill

                print(f"Successfully imported skill: {imported_skill.adapted_name}")
                return True
            else:
                print(f"Failed to import skill: {imported_skill.adapted_name}")
                return False

        except Exception as e:
            print(f"Error importing skill {imported_skill.adapted_name}: {e}")
            return False

    def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of the integration"""
        return {
            'external_sources': len(self.discovery_engine.sources),
            'active_sources': sum(1 for s in self.discovery_engine.sources.values() if s.active),
            'discovered_skills': len(self.discovery_engine.discovered_skills),
            'current_conflicts': len(self.conflict_resolver.conflicts),
            'adaptive_skills': len(self.adaptive_manager.skill_registry),
            'sources': [
                {
                    'name': source.name,
                    'type': source.source_type,
                    'url': source.url,
                    'active': source.active,
                    'last_scanned': source.last_scanned,
                    'skill_count': source.skill_count
                }
                for source in self.discovery_engine.sources.values()
            ]
        }

    def discover_credit_card_security_skills(self) -> None:
        """Add predefined sources for credit card and security skills"""
        security_sources = [
            {
                'name': 'OWASP_Cheat_Sheet',
                'url': 'https://cheatsheetseries.owasp.org/cheatsheets/Credit_Card_Cheat_Sheet.html',
                'source_type': 'documentation',
                'description': 'OWASP Credit Card Security Guidelines',
                'tags': ['security', 'credit_card', 'owasp', 'best_practices']
            },
            {
                'name': 'PCI_DSS_Docs',
                'url': 'https://docs.pcisecuritystandards.org/',
                'source_type': 'documentation',
                'description': 'PCI DSS Security Standards Documentation',
                'tags': ['security', 'pci_dss', 'compliance', 'credit_card']
            },
            {
                'name': 'Python_Regex_Docs',
                'url': 'https://docs.python.org/3/library/re.html',
                'source_type': 'documentation',
                'description': 'Python Regular Expression Documentation',
                'tags': ['python', 'regex', 'pattern_matching', 'programming']
            }
        ]

        for source_data in security_sources:
            self.add_external_source(**source_data)