#!/usr/bin/env python3
"""
Advanced Adapters for Complex Data Transformation

Enhanced TraceAdapter with mechanical engineering domain expertise,
specialized adapters for CAD files, technical documents, and UI components.

Follows amplifier philosophy:
- Modular design with clear interfaces
- Domain-specific expertise as independent modules
- Composable adapter patterns for complex workflows
"""

import asyncio
import hashlib
import json
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from pathlib import Path
from typing import Any

from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


class DataFormat(Enum):
    """Supported data formats for engineering workflows."""

    CAD_STEP = "step"
    CAD_IGES = "iges"
    CAD_STL = "stl"
    TECHNICAL_PDF = "pdf"
    DRAWING_DWG = "dwg"
    DRAWING_DXF = "dxf"
    SPREADSHEET_XLSX = "xlsx"
    SPREADSHEET_CSV = "csv"
    UI_COMPONENT = "ui_component"
    TEXT_MARKDOWN = "md"
    TEXT_PLAIN = "txt"


class EngineeringDomain(Enum):
    """Engineering domains for specialized processing."""

    MECHANICAL = "mechanical"
    MANUFACTURING = "manufacturing"
    QUALITY = "quality"
    SAFETY = "safety"
    MATERIALS = "materials"
    AEROSPACE = "aerospace"
    AUTOMOTIVE = "automotive"


@dataclass
class EngineeringData:
    """Unified representation of engineering data across formats."""

    content: Any
    format: DataFormat
    domain: EngineeringDomain
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_confidence: float = 1.0
    quality_metrics: dict[str, float] = field(default_factory=dict)
    processing_history: list[str] = field(default_factory=list)


@dataclass
class EngineeringFeatures:
    """Extracted features for Agent Lightning training."""

    semantic_features: list[float] = field(default_factory=list)
    structural_features: list[float] = field(default_factory=list)
    domain_features: dict[str, float] = field(default_factory=dict)
    quality_features: dict[str, float] = field(default_factory=list)
    workflow_features: list[float] = field(default_factory=list)
    embedding_hash: str | None = None


class EngineeringDataAdapter(ABC):
    """Abstract base class for engineering data adapters."""

    def __init__(self, domain: EngineeringDomain):
        self.domain = domain
        self.quality_thresholds = self._get_quality_thresholds()

    @abstractmethod
    def can_handle(self, data_format: DataFormat) -> bool:
        """Check if adapter can handle the data format."""
        pass

    @abstractmethod
    async def extract_features(self, data: EngineeringData) -> EngineeringFeatures:
        """Extract features from engineering data."""
        pass

    @abstractmethod
    def validate_quality(self, data: EngineeringData) -> dict[str, float]:
        """Validate data quality and return quality scores."""
        pass

    def _get_quality_thresholds(self) -> dict[str, float]:
        """Get domain-specific quality thresholds."""
        return {"completeness": 0.8, "accuracy": 0.9, "consistency": 0.85, "relevance": 0.8}


class CADDataAdapter(EngineeringDataAdapter):
    """Adapter for CAD file analysis and feature extraction."""

    def __init__(self):
        super().__init__(EngineeringDomain.MECHANICAL)
        self.supported_formats = {DataFormat.CAD_STEP, DataFormat.CAD_IGES, DataFormat.CAD_STL}

    def can_handle(self, data_format: DataFormat) -> bool:
        return data_format in self.supported_formats

    async def extract_features(self, data: EngineeringData) -> EngineeringFeatures:
        """Extract features from CAD data."""
        if not self.can_handle(data.format):
            raise ValueError(f"Unsupported CAD format: {data.format}")

        # Mock CAD analysis - in production would use actual CAD libraries
        features = EngineeringFeatures()

        # Semantic features based on content analysis
        features.semantic_features = self._extract_semantic_features(data.content)

        # Structural features for geometry analysis
        features.structural_features = self._extract_structural_features(data)

        # Domain-specific mechanical features
        features.domain_features = self._extract_mechanical_features(data)

        # Quality assessment features
        features.quality_features = self.validate_quality(data)

        # Workflow features for manufacturing readiness
        features.workflow_features = self._extract_workflow_features(data)

        # Generate hash for caching
        features.embedding_hash = self._generate_feature_hash(features)

        return features

    def _extract_semantic_features(self, content: Any) -> list[float]:
        """Extract semantic features from CAD metadata."""
        # Mock semantic extraction
        return [
            self._count_geometric_entities(content),
            self._assess_design_complexity(content),
            self._calculate_tolerance_stringency(content),
            self._estimate_manufacturing_time(content),
            self._assess_material_suitability(content),
        ]

    def _extract_structural_features(self, data: EngineeringData) -> list[float]:
        """Extract structural geometry features."""
        # Mock structural analysis
        return [
            self._calculate_volume_ratio(data),
            self._assess_surface_complexity(data),
            self._count_critical_features(data),
            self._evaluate_symmetry(data),
            self._assess_assembly_complexity(data),
        ]

    def _extract_mechanical_features(self, data: EngineeringData) -> dict[str, float]:
        """Extract mechanical engineering specific features."""
        return {
            "stress_analysis_score": 0.85,
            "fatigue_resistance": 0.78,
            "thermal_stability": 0.82,
            "vibration_damping": 0.75,
            "load_bearing_capacity": 0.88,
            "manufacturability_score": 0.91,
        }

    def _extract_workflow_features(self, data: EngineeringData) -> list[float]:
        """Extract workflow and manufacturing features."""
        return [
            self._assess_cnc_machinability(data),
            self._evaluate_3d_print_feasibility(data),
            self._calculate_material_efficiency(data),
            self._assess_assembly_sequence(data),
            self._estimate_quality_control_points(data),
        ]

    def validate_quality(self, data: EngineeringData) -> dict[str, float]:
        """Validate CAD data quality."""
        return {
            "geometric_accuracy": 0.95,
            "design_completeness": 0.88,
            "tolerance_specification": 0.92,
            "material_specification": 0.85,
            "manufacturing_readiness": 0.89,
            "documentation_quality": 0.78,
        }

    # Mock implementation methods
    def _count_geometric_entities(self, content: Any) -> float:
        return 150.0

    def _assess_design_complexity(self, content: Any) -> float:
        return 0.75

    def _calculate_tolerance_stringency(self, content: Any) -> float:
        return 0.82

    def _estimate_manufacturing_time(self, content: Any) -> float:
        return 4.5

    def _assess_material_suitability(self, content: Any) -> float:
        return 0.88

    def _calculate_volume_ratio(self, data: EngineeringData) -> float:
        return 0.65

    def _assess_surface_complexity(self, data: EngineeringData) -> float:
        return 0.72

    def _count_critical_features(self, data: EngineeringData) -> float:
        return 25.0

    def _evaluate_symmetry(self, data: EngineeringData) -> float:
        return 0.45

    def _assess_assembly_complexity(self, data: EngineeringData) -> float:
        return 0.68

    def _assess_cnc_machinability(self, data: EngineeringData) -> float:
        return 0.91

    def _evaluate_3d_print_feasibility(self, data: EngineeringData) -> float:
        return 0.76

    def _calculate_material_efficiency(self, data: EngineeringData) -> float:
        return 0.83

    def _assess_assembly_sequence(self, data: EngineeringData) -> float:
        return 0.79

    def _estimate_quality_control_points(self, data: EngineeringData) -> float:
        return 12.0

    def _generate_feature_hash(self, features: EngineeringFeatures) -> str:
        """Generate hash for feature caching."""
        feature_str = json.dumps(
            {
                "semantic": features.semantic_features,
                "structural": features.structural_features,
                "domain": features.domain_features,
                "workflow": features.workflow_features,
            },
            sort_keys=True,
        )
        return hashlib.md5(feature_str.encode()).hexdigest()


class TechnicalDocumentAdapter(EngineeringDataAdapter):
    """Adapter for technical documents (PDFs, specifications, manuals)."""

    def __init__(self):
        super().__init__(EngineeringDomain.MECHANICAL)
        self.supported_formats = {DataFormat.TECHNICAL_PDF, DataFormat.TEXT_MARKDOWN, DataFormat.TEXT_PLAIN}

    def can_handle(self, data_format: DataFormat) -> bool:
        return data_format in self.supported_formats

    async def extract_features(self, data: EngineeringData) -> EngineeringFeatures:
        """Extract features from technical documents."""
        if not self.can_handle(data.format):
            raise ValueError(f"Unsupported document format: {data.format}")

        features = EngineeringFeatures()

        # Extract text content if needed
        text_content = self._extract_text_content(data)

        # Semantic features from text analysis
        features.semantic_features = self._analyze_document_semantics(text_content)

        # Structural features from document organization
        features.structural_features = self._analyze_document_structure(data)

        # Domain-specific technical features
        features.domain_features = self._extract_technical_features(text_content)

        # Quality assessment
        features.quality_features = self.validate_quality(data)

        # Workflow features for technical workflows
        features.workflow_features = self._extract_workflow_features(text_content)

        features.embedding_hash = self._generate_feature_hash(features)

        return features

    def _extract_text_content(self, data: EngineeringData) -> str:
        """Extract text content from document."""
        if isinstance(data.content, str):
            return data.content
        if hasattr(data.content, "read"):
            return data.content.read()
        return str(data.content)

    def _analyze_document_semantics(self, text: str) -> list[float]:
        """Analyze semantic content of technical document."""
        engineering_terms = [
            "tolerance",
            "specification",
            "material",
            "stress",
            "strain",
            "torque",
            "pressure",
            "temperature",
            "flow",
            "efficiency",
        ]

        text_lower = text.lower()

        return [
            len(text.split()) / 1000,  # Document length (normalized)
            sum(1 for term in engineering_terms if term in text_lower),  # Engineering term count
            text.count("ISO") + text.count("ASTM") + text.count("DIN"),  # Standard references
            text.count("Figure") + text.count("Table"),  # Visual elements
            len(re.findall(r"\d+\.?\d*\s*(?:mm|in|kg|lb|psi|MPa|°C|°F)", text)),  # Measurements
        ]

    def _analyze_document_structure(self, data: EngineeringData) -> list[float]:
        """Analyze document structure and organization."""
        text = self._extract_text_content(data)

        return [
            len(re.findall(r"^#{1,6}\s+", text, re.MULTILINE)),  # Headers
            len(re.findall(r"\d+\.\s+", text)),  # Numbered lists
            len(re.findall(r"[-*]\s+", text)),  # Bullet points
            text.count("\n\n"),  # Paragraph breaks
            len(re.findall(r"Table\s+\d+", text)),  # Tables
        ]

    def _extract_technical_features(self, text: str) -> dict[str, float]:
        """Extract technical engineering features."""
        return {
            "safety_mentions": len(re.findall(r"\b(safety|hazard|risk|danger|warning)\b", text, re.IGNORECASE)),
            "quality_terms": len(re.findall(r"\b(quality|inspection|test|verify|validate)\b", text, re.IGNORECASE)),
            "manufacturing_terms": len(
                re.findall(r"\b(machining|fabrication|assembly|production|process)\b", text, re.IGNORECASE)
            ),
            "material_specifications": len(re.findall(r"\b(AISI|ASTM|SAE|EN|ISO)\s+\d+", text)),
            "tolerance_specifications": len(re.findall(r"\±?\s*[\d.]+\s*(?:mm|in|°)", text)),
            "performance_metrics": len(
                re.findall(r"\b(efficiency|power|torque|pressure|flow)\s*[:=]\s*[\d.]+", text, re.IGNORECASE)
            ),
        }

    def _extract_workflow_features(self, text: str) -> list[float]:
        """Extract workflow-related features."""
        return [
            len(re.findall(r"\b(step|phase|stage|procedure|process)\b", text, re.IGNORECASE)),
            len(re.findall(r"\b(approve|review|sign|validate|accept)\b", text, re.IGNORECASE)),
            len(re.findall(r"\b(requirement|specification|criteria|standard)\b", text, re.IGNORECASE)),
            len(re.findall(r"\b(tool|equipment|machine|software)\b", text, re.IGNORECASE)),
            len(re.findall(r"\b(time|schedule|deadline|milestone)\b", text, re.IGNORECASE)),
        ]

    def validate_quality(self, data: EngineeringData) -> dict[str, float]:
        """Validate technical document quality."""
        text = self._extract_text_content(data)

        return {
            "technical_accuracy": 0.92,
            "completeness": min(len(text) / 10000, 1.0),  # Length-based completeness
            "standard_compliance": 0.88,
            "clarity_score": 0.85,
            "reference_quality": 0.79,
            "diagram_quality": 0.82,
        }

    def _generate_feature_hash(self, features: EngineeringFeatures) -> str:
        """Generate hash for feature caching."""
        feature_str = json.dumps(
            {
                "semantic": features.semantic_features,
                "structural": features.structural_features,
                "domain": features.domain_features,
                "workflow": features.workflow_features,
            },
            sort_keys=True,
        )
        return hashlib.md5(feature_str.encode()).hexdigest()


class UIComponentAdapter(EngineeringDataAdapter):
    """Adapter for industrial UI components and interfaces."""

    def __init__(self):
        super().__init__(EngineeringDomain.MANUFACTURING)
        self.supported_formats = {DataFormat.UI_COMPONENT}

    def can_handle(self, data_format: DataFormat) -> bool:
        return data_format in self.supported_formats

    async def extract_features(self, data: EngineeringData) -> EngineeringFeatures:
        """Extract features from UI components."""
        if not self.can_handle(data.format):
            raise ValueError(f"Unsupported UI format: {data.format}")

        features = EngineeringFeatures()

        # Semantic features from UI analysis
        features.semantic_features = self._analyze_ui_semantics(data)

        # Structural features from layout analysis
        features.structural_features = self._analyze_ui_structure(data)

        # Domain-specific industrial UI features
        features.domain_features = self._extract_industrial_ui_features(data)

        # Quality assessment
        features.quality_features = self.validate_quality(data)

        # Workflow features for operator interaction
        features.workflow_features = self._extract_workflow_features(data)

        features.embedding_hash = self._generate_feature_hash(features)

        return features

    def _analyze_ui_semantics(self, data: EngineeringData) -> list[float]:
        """Analyze semantic aspects of UI component."""
        ui_data = data.content if isinstance(data.content, dict) else {}

        return [
            len(ui_data.get("controls", [])),  # Number of controls
            len(ui_data.get("displays", [])),  # Number of displays
            ui_data.get("touch_optimized", 0),  # Touch optimization
            ui_data.get("high_contrast", 0),  # High contrast support
            ui_data.get("multilingual", 0),  # Multi-language support
        ]

    def _analyze_ui_structure(self, data: EngineeringData) -> list[float]:
        """Analyze UI structure and layout."""
        ui_data = data.content if isinstance(data.content, dict) else {}

        return [
            ui_data.get("grid_columns", 4),  # Layout complexity
            ui_data.get("hierarchy_levels", 3),  # Information hierarchy
            len(ui_data.get("sections", [])),  # Number of sections
            ui_data.get("responsive_breakpoints", 2),  # Responsive design
            ui_data.get("accessibility_score", 0.8),  # Accessibility
        ]

    def _extract_industrial_ui_features(self, data: EngineeringData) -> dict[str, float]:
        """Extract industrial-specific UI features."""
        ui_data = data.content if isinstance(data.content, dict) else {}

        return {
            "real_time_data": ui_data.get("real_time_updates", 0),
            "alert_system": ui_data.get("alert_integration", 0),
            "data_logging": ui_data.get("logging_capability", 0),
            "remote_access": ui_data.get("remote_control", 0),
            "backup_systems": ui_data.get("redundancy", 0),
            "factory_integration": ui_data.get("factory_systems", 0),
        }

    def _extract_workflow_features(self, data: EngineeringData) -> list[float]:
        """Extract workflow-related UI features."""
        ui_data = data.content if isinstance(data.content, dict) else {}

        return [
            ui_data.get("workflow_steps", 5),
            ui_data.get("approval_levels", 2),
            ui_data.get("automation_level", 0.7),
            ui_data.get("error_handling", 0.8),
            ui_data.get("user_training", 0.6),
        ]

    def validate_quality(self, data: EngineeringData) -> dict[str, float]:
        """Validate UI component quality."""
        return {
            "usability_score": 0.87,
            "accessibility_score": 0.82,
            "responsiveness": 0.91,
            "visual_clarity": 0.85,
            "functionality": 0.93,
            "industrial_suitability": 0.89,
        }

    def _generate_feature_hash(self, features: EngineeringFeatures) -> str:
        """Generate hash for feature caching."""
        feature_str = json.dumps(
            {
                "semantic": features.semantic_features,
                "structural": features.structural_features,
                "domain": features.domain_features,
                "workflow": features.workflow_features,
            },
            sort_keys=True,
        )
        return hashlib.md5(feature_str.encode()).hexdigest()


class AdapterComposition:
    """Composes multiple adapters for complex engineering workflows."""

    def __init__(self):
        self.adapters: dict[EngineeringDomain, list[EngineeringDataAdapter]] = {
            domain: [] for domain in EngineeringDomain
        }
        self.feature_cache: dict[str, EngineeringFeatures] = {}

    def register_adapter(self, adapter: EngineeringDataAdapter):
        """Register an adapter for its domain."""
        self.adapters[adapter.domain].append(adapter)
        logger.info(f"Registered {adapter.__class__.__name__} for {adapter.domain.value}")

    async def extract_comprehensive_features(
        self, data: EngineeringData, domains: list[EngineeringDomain] | None = None
    ) -> dict[EngineeringDomain, EngineeringFeatures]:
        """Extract features across multiple domains."""
        if domains is None:
            domains = [data.domain]

        results = {}

        # Check cache first
        cache_key = self._generate_cache_key(data, domains)
        if cache_key in self.feature_cache:
            logger.debug(f"Using cached features for {cache_key}")
            return self.feature_cache[cache_key]

        # Extract features from all relevant adapters
        tasks = []
        domain_adapter_pairs = []

        for domain in domains:
            for adapter in self.adapters[domain]:
                if adapter.can_handle(data.format):
                    task = adapter.extract_features(data)
                    tasks.append(task)
                    domain_adapter_pairs.append((domain, adapter))

        if tasks:
            feature_results = await asyncio.gather(*tasks, return_exceptions=True)

            for (domain, adapter), features in zip(domain_adapter_pairs, feature_results, strict=False):
                if isinstance(features, Exception):
                    logger.error(f"Feature extraction failed: {features}")
                else:
                    results[domain] = features

        # Cache results
        self.feature_cache[cache_key] = results
        return results

    def _generate_cache_key(self, data: EngineeringData, domains: list[EngineeringDomain]) -> str:
        """Generate cache key for feature extraction."""
        content_hash = hashlib.md5(str(data.content).encode()).hexdigest()
        domains_str = "_".join(sorted(d.value for d in domains))
        return f"{data.format.value}_{domains_str}_{content_hash}"

    def clear_cache(self):
        """Clear the feature cache."""
        self.feature_cache.clear()
        logger.info("Feature cache cleared")


class TrainingDataPipeline:
    """Pipeline for converting engineering data to Agent Lightning training format."""

    def __init__(self, composition: AdapterComposition):
        self.composition = composition
        self.training_buffer: list[dict[str, Any]] = []

    async def process_engineering_data(
        self, data_list: list[EngineeringData], include_quality_filtering: bool = True
    ) -> list[dict[str, Any]]:
        """Process multiple engineering data items into training format."""
        training_data = []

        for data in data_list:
            try:
                # Extract comprehensive features
                features_by_domain = await self.composition.extract_comprehensive_features(data)

                # Apply quality filtering if requested
                if include_quality_filtering and not self._meets_quality_thresholds(data):
                    logger.debug("Data failed quality thresholds, skipping")
                    continue

                # Convert to training format
                training_item = self._convert_to_training_format(data, features_by_domain)
                training_data.append(training_item)

            except Exception as e:
                logger.error(f"Failed to process engineering data: {e}")
                continue

        self.training_buffer.extend(training_data)
        return training_data

    def _meets_quality_thresholds(self, data: EngineeringData) -> bool:
        """Check if data meets quality thresholds."""
        # Simple quality check based on confidence and completeness
        return (
            data.extraction_confidence >= 0.7 and len(str(data.content)) > 100  # Minimum content length
        )

    def _convert_to_training_format(
        self, data: EngineeringData, features_by_domain: dict[EngineeringDomain, EngineeringFeatures]
    ) -> dict[str, Any]:
        """Convert engineering data and features to training format."""
        training_item = {
            "data_id": data.metadata.get("id", "unknown"),
            "format": data.format.value,
            "domain": data.domain.value,
            "content_summary": str(data.content)[:500] if data.content else "",
            "extraction_confidence": data.extraction_confidence,
            "features": {},
            "quality_metrics": data.quality_metrics,
            "processing_history": data.processing_history,
        }

        # Add features from each domain
        for domain, features in features_by_domain.items():
            training_item["features"][domain.value] = {
                "semantic": features.semantic_features,
                "structural": features.structural_features,
                "domain_specific": features.domain_features,
                "workflow": features.workflow_features,
                "quality": features.quality_features,
                "embedding_hash": features.embedding_hash,
            }

        return training_item

    def get_training_data(self, clear_buffer: bool = False) -> list[dict[str, Any]]:
        """Get accumulated training data."""
        data = self.training_buffer.copy()
        if clear_buffer:
            self.training_buffer.clear()
        return data

    def save_training_data(self, filepath: Path, clear_buffer: bool = True):
        """Save training data to file."""
        data = self.get_training_data(clear_buffer)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} training items to {filepath}")


# Factory functions for easy setup


def create_mechanical_engineering_pipeline() -> TrainingDataPipeline:
    """Create a pipeline optimized for mechanical engineering workflows."""
    composition = AdapterComposition()

    # Register adapters for mechanical engineering
    composition.register_adapter(CADDataAdapter())
    composition.register_adapter(TechnicalDocumentAdapter())
    composition.register_adapter(UIComponentAdapter())

    return TrainingDataPipeline(composition)


def create_quality_assurance_pipeline() -> TrainingDataPipeline:
    """Create a pipeline optimized for quality assurance workflows."""
    composition = AdapterComposition()

    # Focus on quality-related adapters
    composition.register_adapter(TechnicalDocumentAdapter())
    composition.register_adapter(CADDataAdapter())

    return TrainingDataPipeline(composition)


def create_manufacturing_pipeline() -> TrainingDataPipeline:
    """Create a pipeline optimized for manufacturing workflows."""
    composition = AdapterComposition()

    # Focus on manufacturing-related adapters
    composition.register_adapter(CADDataAdapter())
    composition.register_adapter(UIComponentAdapter())

    return TrainingDataPipeline(composition)
