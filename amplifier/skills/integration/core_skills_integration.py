"""
Integration with Microsoft Amplifier's 7/7 Core Skills System

This module provides seamless integration between the Skill Seekers technical data
processing capabilities and Microsoft Amplifier's existing 7/7 core skills framework.

The 7/7 Core Skills System:
1. Domain Expertise (Theme Factory, etc.)
2. Core Technology (Database, NodeJS, TypeScript, etc.)
3. Integration (API Design, Full Stack, etc.)
4. Meta Skills (Routing, Testing, etc.)
5. Resource Optimization (Memory, Performance, etc.)
6. JIT Compilation (Dynamic skill compilation)
7. Signature Framework (Zero-hallucination, BootstrapFewShot)
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass
from enum import Enum

# Import core skill frameworks
try:
    from .. import (
        ThemeFactorySkill,
        DatabaseDesignExpertSkill,
        NodeJSExpertSkill,
        TypeScriptExpertSkill,
        ViteExpertSkill,
        PerformanceTestingExpertSkill,
        FullStackIntegrationExpertSkill,
        ApiDesignExpertSkill,
        GraphQLExpertSkill,
    )
    from ..signature_framework import (
        SignatureSkill,
        SkillConfig,
        SkillRole,
        CompositionStrategy,
        ZeroHallucinationEnforcer,
        get_bootstrap_optimizer,
        create_meta_skill,
    )

    CORE_SKILLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Core skills not fully available: {e}")
    CORE_SKILLS_AVAILABLE = False

# Import our integration modules
from .skill_seekers_integration import SkillSeekersIntegrationSkill
from .technical_data_pipeline import TechnicalDataPipeline
from .ast_conflict_analyzer import ASTAnalyzer, ConflictDetector
from .skill_packager import SkillPackager, SkillMetadata


class CoreSkillCategory(Enum):
    """Categories of core skills in the 7/7 system."""

    DOMAIN_EXPERTISE = "domain_expertise"
    CORE_TECHNOLOGY = "core_technology"
    INTEGRATION = "integration"
    META_SKILLS = "meta_skills"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    JIT_COMPILATION = "jit_compilation"
    SIGNATURE_FRAMEWORK = "signature_framework"


@dataclass
class SkillEnhancementRequest:
    """Request for enhancing a core skill with technical data."""

    base_skill_type: str
    enhancement_data_sources: List[Dict[str, Any]]
    enhancement_level: str  # "basic", "standard", "advanced"
    conflict_resolution: str  # "merge", "replace", "hybrid"
    quality_threshold: float = 0.7
    preserve_original: bool = True


@dataclass
class EnhancedSkill:
    """Result of core skill enhancement."""

    original_skill_type: str
    enhanced_skill_class: Type[SignatureSkill]
    enhancement_metadata: Dict[str, Any]
    quality_improvement: float
    new_capabilities: List[str]
    conflicts_resolved: int
    processing_time: float


class CoreSkillsIntegrator:
    """
    Integrates Skill Seekers capabilities with Microsoft Amplifier's 7/7 core skills.

    This integrator provides:
    - Dynamic enhancement of existing core skills
    - Technical data integration into core skills
    - Conflict resolution between enhanced skills
    - Quality assessment and optimization
    - Seamless compatibility with existing skill framework
    """

    def __init__(self):
        self.core_skill_registry = {}
        self.enhanced_skills = {}
        self.integration_pipeline = None
        self.skill_packager = None

        # Initialize core skill mappings
        self._initialize_core_skill_mappings()

        # Initialize integration components
        self._initialize_integration_components()

    def _initialize_core_skill_mappings(self):
        """Initialize mappings of core skill types to their classes."""
        if CORE_SKILLS_AVAILABLE:
            self.core_skill_registry = {
                # Domain Expertise
                "theme_factory": ThemeFactorySkill,
                # Core Technology
                "database_design": DatabaseDesignExpertSkill,
                "nodejs_expert": NodeJSExpertSkill,
                "typescript_expert": TypeScriptExpertSkill,
                "vite_expert": ViteExpertSkill,
                "performance_testing": PerformanceTestingExpertSkill,
                # Integration
                "full_stack_integration": FullStackIntegrationExpertSkill,
                "api_design": ApiDesignExpertSkill,
                "graphql_expert": GraphQLExpertSkill,
            }

    async def _initialize_integration_components(self):
        """Initialize integration components."""
        try:
            self.integration_pipeline = TechnicalDataPipeline()
            await self.integration_pipeline.initialize()

            self.skill_packager = SkillPackager()

            logging.info("Core skills integration components initialized")

        except Exception as e:
            logging.error(f"Failed to initialize integration components: {e}")
            raise

    async def enhance_core_skill(self, request: SkillEnhancementRequest) -> EnhancedSkill:
        """
        Enhance a core skill with technical data from various sources.

        Args:
            request: Enhancement request with data sources and configuration

        Returns:
            EnhancedSkill: Result of skill enhancement
        """
        start_time = asyncio.get_event_loop().time()

        try:
            logging.info(f"Enhancing core skill: {request.base_skill_type}")

            # Step 1: Get the base skill class
            base_skill_class = self._get_base_skill_class(request.base_skill_type)
            if not base_skill_class:
                raise ValueError(f"Unknown core skill type: {request.base_skill_type}")

            # Step 2: Process technical data sources
            enhancement_data = await self._process_enhancement_data(
                request.enhancement_data_sources, request.base_skill_type
            )

            # Step 3: Create enhanced skill class
            enhanced_skill_class = await self._create_enhanced_skill_class(base_skill_class, enhancement_data, request)

            # Step 4: Validate enhanced skill
            validation_result = await self._validate_enhanced_skill(enhanced_skill_class)

            # Step 5: Calculate quality improvement
            quality_improvement = await self._calculate_quality_improvement(
                base_skill_class, enhanced_skill_class, enhancement_data
            )

            processing_time = asyncio.get_event_loop().time() - start_time

            result = EnhancedSkill(
                original_skill_type=request.base_skill_type,
                enhanced_skill_class=enhanced_skill_class,
                enhancement_metadata={
                    "data_sources_processed": len(request.enhancement_data_sources),
                    "enhancement_level": request.enhancement_level,
                    "validation_result": validation_result,
                    "processing_time": processing_time,
                },
                quality_improvement=quality_improvement,
                new_capabilities=await self._identify_new_capabilities(enhanced_skill_class),
                conflicts_resolved=len(enhancement_data.get("conflicts_resolved", [])),
                processing_time=processing_time,
            )

            # Store enhanced skill
            self.enhanced_skills[f"{request.base_skill_type}_enhanced"] = result

            logging.info(f"Core skill enhancement completed: {request.base_skill_type}")
            return result

        except Exception as e:
            logging.error(f"Failed to enhance core skill {request.base_skill_type}: {e}")
            raise

    def _get_base_skill_class(self, skill_type: str) -> Optional[Type]:
        """Get the base skill class for enhancement."""
        return self.core_skill_registry.get(skill_type)

    async def _process_enhancement_data(self, data_sources: List[Dict[str, Any]], skill_type: str) -> Dict[str, Any]:
        """Process technical data sources for skill enhancement."""
        try:
            # Create enhancement request
            skill_name = f"{skill_type}_enhancement"
            skill_description = f"Enhanced {skill_type} skill with integrated technical data"

            # Use the technical data pipeline
            processing_result = await self.integration_pipeline.process_sources(
                sources=data_sources, skill_name=skill_name, skill_description=skill_description
            )

            # Extract relevant data for enhancement
            enhancement_data = {
                "skill_files": processing_result.generated_files,
                "metadata": processing_result.metadata,
                "conflicts_detected": processing_result.conflicts_detected,
                "quality_score": processing_result.quality_score,
                "conflicts_resolved": [],  # Will be populated during conflict resolution
            }

            return enhancement_data

        except Exception as e:
            logging.error(f"Failed to process enhancement data: {e}")
            raise

    async def _create_enhanced_skill_class(
        self, base_skill_class: Type, enhancement_data: Dict[str, Any], request: SkillEnhancementRequest
    ) -> Type[SignatureSkill]:
        """Create an enhanced skill class by combining base skill with new data."""
        try:
            # Create dynamic skill class
            class_name = f"Enhanced{base_skill_class.__name__}"

            # Get base configuration
            if hasattr(base_skill_class, "config"):
                base_config = base_skill_class.config
            else:
                base_config = SkillConfig(
                    name=class_name, description=f"Enhanced version of {base_skill_class.__name__}", version="2.0.0"
                )

            # Create enhanced configuration
            enhanced_config = SkillConfig(
                name=class_name,
                description=f"{base_config.description} with integrated technical knowledge",
                version="2.0.0",
                priority=base_config.priority,
                enhancement_level=request.enhancement_level,
                additional_metadata={
                    "base_skill": base_skill_class.__name__,
                    "enhancement_sources": len(request.enhancement_data_sources),
                    "quality_score": enhancement_data["quality_score"],
                },
            )

            # Create the enhanced skill class
            enhanced_skill = type(
                class_name,
                (base_skill_class, SkillSeekersIntegrationSkill),
                {
                    "config": enhanced_config,
                    "enhancement_data": enhancement_data,
                    "__init__": self._create_enhanced_init_method(base_skill_class, enhancement_data),
                    "execute": self._create_enhanced_execute_method(base_skill_class, enhancement_data),
                },
            )

            return enhanced_skill

        except Exception as e:
            logging.error(f"Failed to create enhanced skill class: {e}")
            raise

    def _create_enhanced_init_method(self, base_class: Type, enhancement_data: Dict[str, Any]):
        """Create enhanced initialization method."""

        def __init__(self):
            # Initialize base skill
            if hasattr(base_class, "__init__"):
                base_class.__init__(self)

            # Initialize enhancement data
            self.enhancement_data = enhancement_data
            self.skill_files = enhancement_data["skill_files"]
            self.technical_knowledge = enhancement_data["skill_files"].get("SKILL.md", "")

        return __init__

    def _create_enhanced_execute_method(self, base_class: Type, enhancement_data: Dict[str, Any]):
        """Create enhanced execute method that combines both skills."""

        async def execute(self, *args, **kwargs):
            # Execute base skill logic
            if hasattr(base_class, "execute"):
                base_result = await base_class.execute(self, *args, **kwargs)
            else:
                base_result = None

            # Add technical knowledge from enhancement
            if hasattr(self, "technical_knowledge") and self.technical_knowledge:
                # Integrate technical knowledge into response
                if base_result and hasattr(base_result, "content"):
                    enhanced_content = f"{base_result.content}\n\n# Technical Knowledge\n{self.technical_knowledge}"
                    if hasattr(base_result, "content"):
                        base_result.content = enhanced_content

            return base_result

        return execute

    async def _validate_enhanced_skill(self, enhanced_skill_class: Type) -> Dict[str, Any]:
        """Validate the enhanced skill class."""
        validation_result = {"is_valid": True, "errors": [], "warnings": []}

        try:
            # Check if skill can be instantiated
            instance = enhanced_skill_class()

            # Check if required methods exist
            required_methods = ["execute"]
            for method in required_methods:
                if not hasattr(instance, method):
                    validation_result["errors"].append(f"Missing required method: {method}")
                    validation_result["is_valid"] = False

            # Check if enhancement data is accessible
            if not hasattr(instance, "enhancement_data"):
                validation_result["warnings"].append("Enhancement data not accessible")

        except Exception as e:
            validation_result["errors"].append(f"Validation error: {e}")
            validation_result["is_valid"] = False

        return validation_result

    async def _calculate_quality_improvement(
        self, base_skill_class: Type, enhanced_skill_class: Type, enhancement_data: Dict[str, Any]
    ) -> float:
        """Calculate quality improvement from enhancement."""
        try:
            base_quality = 0.5  # Assume base quality
            enhanced_quality = enhancement_data.get("quality_score", 0.5)

            improvement = enhanced_quality - base_quality
            return max(0.0, min(1.0, improvement))

        except Exception as e:
            logging.warning(f"Failed to calculate quality improvement: {e}")
            return 0.0

    async def _identify_new_capabilities(self, enhanced_skill_class: Type) -> List[str]:
        """Identify new capabilities added by enhancement."""
        capabilities = []

        try:
            instance = enhanced_skill_class()

            # Check for enhancement-specific attributes
            if hasattr(instance, "skill_files"):
                capabilities.append("Integrated technical documentation")

            if hasattr(instance, "technical_knowledge") and instance.technical_knowledge:
                capabilities.append("Enhanced technical knowledge base")

            # Check for file-based references
            if hasattr(instance, "enhancement_data"):
                files = instance.enhancement_data.get("skill_files", {})
                if any("references/" in key for key in files.keys()):
                    capabilities.append("Comprehensive reference materials")

        except Exception as e:
            logging.warning(f"Failed to identify new capabilities: {e}")

        return capabilities

    async def create_unified_skill(
        self, skill_types: List[str], unified_name: str, conflict_resolution: str = "merge"
    ) -> Type[SignatureSkill]:
        """
        Create a unified skill from multiple core skills.

        Args:
            skill_types: List of core skill types to unify
            unified_name: Name for the unified skill
            conflict_resolution: Strategy for resolving conflicts

        Returns:
            Type[SignatureSkill]: Unified skill class
        """
        try:
            logging.info(f"Creating unified skill: {unified_name}")

            # Get skill classes
            skill_classes = []
            for skill_type in skill_types:
                skill_class = self._get_base_skill_class(skill_type)
                if skill_class:
                    skill_classes.append(skill_class)
                else:
                    # Check for enhanced versions
                    enhanced_key = f"{skill_type}_enhanced"
                    if enhanced_key in self.enhanced_skills:
                        skill_classes.append(self.enhanced_skills[enhanced_key].enhanced_skill_class)

            if len(skill_classes) < 2:
                raise ValueError("Need at least 2 skills to create unified skill")

            # Create unified skill using signature framework
            if CORE_SKILLS_AVAILABLE:
                unified_skill = await create_meta_skill(
                    name=unified_name,
                    component_skills=skill_classes,
                    composition_strategy=CompositionStrategy.SEQUENTIAL,
                    conflict_resolution=conflict_resolution,
                )
            else:
                # Fallback: create simple combined skill
                unified_skill = self._create_fallback_unified_skill(skill_classes, unified_name)

            logging.info(f"Unified skill created: {unified_name}")
            return unified_skill

        except Exception as e:
            logging.error(f"Failed to create unified skill {unified_name}: {e}")
            raise

    def _create_fallback_unified_skill(self, skill_classes: List[Type], unified_name: str) -> Type[SignatureSkill]:
        """Create fallback unified skill when signature framework is not available."""

        class UnifiedSkill(SignatureSkill):
            def __init__(self):
                config = SkillConfig(
                    name=unified_name,
                    description=f"Unified skill combining {len(skill_classes)} core skills",
                    version="1.0.0",
                )
                super().__init__(config)
                self.component_skills = [cls() for cls in skill_classes]

            async def execute(self, *args, **kwargs):
                results = []
                for skill in self.component_skills:
                    if hasattr(skill, "execute"):
                        result = await skill.execute(*args, **kwargs)
                        results.append(result)
                return results

        return UnifiedSkill

    async def batch_enhance_skills(self, enhancement_requests: List[SkillEnhancementRequest]) -> List[EnhancedSkill]:
        """Enhance multiple core skills in batch."""
        tasks = []
        for request in enhancement_requests:
            task = self.enhance_core_skill(request)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        enhanced_skills = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Failed to enhance skill {enhancement_requests[i].base_skill_type}: {result}")
            else:
                enhanced_skills.append(result)

        return enhanced_skills

    def get_enhanced_skills_overview(self) -> Dict[str, Any]:
        """Get overview of all enhanced skills."""
        overview = {
            "total_enhanced": len(self.enhanced_skills),
            "enhanced_skills": {},
            "quality_improvements": [],
            "new_capabilities_summary": {},
        }

        for skill_key, enhanced_skill in self.enhanced_skills.items():
            overview["enhanced_skills"][skill_key] = {
                "original_type": enhanced_skill.original_skill_type,
                "quality_improvement": enhanced_skill.quality_improvement,
                "new_capabilities_count": len(enhanced_skill.new_capabilities),
                "conflicts_resolved": enhanced_skill.conflicts_resolved,
                "processing_time": enhanced_skill.processing_time,
            }

            overview["quality_improvements"].append(enhanced_skill.quality_improvement)

            for capability in enhanced_skill.new_capabilities:
                if capability not in overview["new_capabilities_summary"]:
                    overview["new_capabilities_summary"][capability] = 0
                overview["new_capabilities_summary"][capability] += 1

        return overview


# Export main classes
__all__ = ["CoreSkillsIntegrator", "SkillEnhancementRequest", "EnhancedSkill", "CoreSkillCategory"]
