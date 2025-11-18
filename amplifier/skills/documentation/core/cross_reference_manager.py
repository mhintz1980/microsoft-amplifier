"""
Cross-Reference Management System

Manages relationships between skills and ensures documentation consistency
across the entire skill ecosystem. Handles compound interactions and
dependency tracking.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import json
import networkx as nx
from collections import defaultdict, deque

from ..utils.token_utils import estimate_tokens


class RelationshipType(Enum):
    """Types of relationships between skills."""

    DEPENDENCY = "dependency"  # Skill A requires Skill B
    EXTENSION = "extension"  # Skill A extends Skill B
    COMPATIBLE = "compatible"  # Skills work well together
    ALTERNATIVE = "alternative"  # Skills provide similar functionality
    SEQUENCE = "sequence"  # Skills typically used in sequence
    COMPOSITION = "composition"  # Skills composed to create functionality
    EXCLUDES = "excludes"  # Skills should not be used together


class RelationshipStrength(Enum):
    """Strength of relationship between skills."""

    WEAK = 1  # Optional relationship
    MODERATE = 2  # Recommended relationship
    STRONG = 3  # Essential relationship
    CRITICAL = 4  # Required relationship


@dataclass
class SkillRelationship:
    """A relationship between two skills."""

    source_skill: str
    target_skill: str
    relationship_type: RelationshipType
    strength: RelationshipStrength
    description: str = ""
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillCluster:
    """A cluster of related skills."""

    name: str
    skills: Set[str] = field(default_factory=set)
    description: str = ""
    common_patterns: List[str] = field(default_factory=list)
    typical_use_cases: List[str] = field(default_factory=list)


@dataclass
class ReferenceValidationResult:
    """Result of cross-reference validation."""

    is_valid: bool
    broken_references: List[str] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    missing_relationships: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    relationship_graph: Optional[nx.DiGraph] = None


class CrossReferenceManager:
    """Manages cross-references and relationships between skills."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent.parent / "data" / "relationships"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.relationships: Dict[str, List[SkillRelationship]] = defaultdict(list)
        self.reverse_relationships: Dict[str, List[SkillRelationship]] = defaultdict(list)
        self.skill_clusters: Dict[str, SkillCluster] = {}
        self.relationship_graph = nx.DiGraph()

        self._load_relationships()

    def add_relationship(self, relationship: SkillRelationship) -> None:
        """Add a relationship between two skills."""

        # Validate skills exist (in a real implementation, would check skill registry)
        self._validate_skill_names(relationship.source_skill, relationship.target_skill)

        # Add to forward and reverse indexes
        self.relationships[relationship.source_skill].append(relationship)
        self.reverse_relationships[relationship.target_skill].append(relationship)

        # Update graph
        self.relationship_graph.add_edge(
            relationship.source_skill,
            relationship.target_skill,
            relationship_type=relationship.relationship_type.value,
            strength=relationship.strength.value,
            description=relationship.description,
        )

        # Add bidirectional edge if specified
        if relationship.bidirectional:
            reverse_relationship = SkillRelationship(
                source_skill=relationship.target_skill,
                target_skill=relationship.source_skill,
                relationship_type=relationship.relationship_type,
                strength=relationship.strength,
                description=relationship.description,
                bidirectional=False,
            )
            self.relationships[relationship.target_skill].append(reverse_relationship)
            self.reverse_relationships[relationship.source_skill].append(reverse_relationship)

            self.relationship_graph.add_edge(
                relationship.target_skill,
                relationship.source_skill,
                relationship_type=relationship.relationship_type.value,
                strength=relationship.strength.value,
                description=relationship.description,
            )

    def get_relationships(
        self, skill_name: str, relationship_type: Optional[RelationshipType] = None
    ) -> List[SkillRelationship]:
        """Get all relationships for a skill, optionally filtered by type."""

        relationships = self.relationships.get(skill_name, [])

        if relationship_type:
            relationships = [r for r in relationships if r.relationship_type == relationship_type]

        return relationships

    def get_related_skills(
        self, skill_name: str, max_depth: int = 2, relationship_types: Optional[List[RelationshipType]] = None
    ) -> Dict[str, List[SkillRelationship]]:
        """Get all related skills up to specified depth."""

        visited = set()
        result = defaultdict(list)
        queue = deque([(skill_name, 0)])

        while queue:
            current_skill, depth = queue.popleft()

            if current_skill in visited or depth > max_depth:
                continue

            visited.add(current_skill)

            # Get relationships for current skill
            skill_relationships = self.relationships.get(current_skill, [])

            for relationship in skill_relationships:
                # Filter by relationship type if specified
                if relationship_types and relationship.relationship_type not in relationship_types:
                    continue

                # Add to result
                result[relationship.target_skill].append(relationship)

                # Add to queue for deeper exploration
                if depth < max_depth:
                    queue.append((relationship.target_skill, depth + 1))

        return dict(result)

    def find_skill_chains(self, start_skill: str, end_skill: str, max_length: int = 5) -> List[List[str]]:
        """Find chains of skills that connect start to end skill."""

        try:
            # Find all paths up to max_length
            paths = list(nx.all_simple_paths(self.relationship_graph, start_skill, end_skill, cutoff=max_length))

            # Sort by length and then by relationship strength
            def path_score(path):
                total_strength = sum(
                    self.relationship_graph.edges[path[i], path[i + 1]]["strength"] for i in range(len(path) - 1)
                )
                return (-len(path), -total_strength)  # Negative for descending sort

            paths.sort(key=path_score)

            return paths[:10]  # Return top 10 paths

        except nx.NetworkXNoPath:
            return []

    def discover_skill_clusters(self, min_cluster_size: int = 3) -> Dict[str, SkillCluster]:
        """Automatically discover clusters of related skills."""

        if len(self.relationship_graph.nodes) < min_cluster_size:
            return {}

        # Use community detection to find clusters
        try:
            # Try to import community detection library
            import networkx.algorithms.community as nx_community

            communities = nx_community.greedy_modularity_communities(self.relationship_graph)

            clusters = {}
            for i, community in enumerate(communities):
                if len(community) >= min_cluster_size:
                    cluster = SkillCluster(
                        name=f"cluster_{i + 1}",
                        skills=set(community),
                        description=f"Auto-discovered cluster {i + 1} with {len(community)} skills",
                    )

                    # Analyze cluster characteristics
                    cluster.common_patterns = self._analyze_cluster_patterns(cluster.skills)
                    cluster.typical_use_cases = self._analyze_cluster_use_cases(cluster.skills)

                    clusters[f"cluster_{i + 1}"] = cluster

                    self.skill_clusters[f"cluster_{i + 1}"] = cluster

            return clusters

        except ImportError:
            # Fallback to simple connected components
            components = list(nx.connected_components(self.relationship_graph.to_undirected()))

            clusters = {}
            for i, component in enumerate(components):
                if len(component) >= min_cluster_size:
                    cluster = SkillCluster(
                        name=f"component_{i + 1}",
                        skills=set(component),
                        description=f"Connected component {i + 1} with {len(component)} skills",
                    )

                    clusters[f"component_{i + 1}"] = cluster
                    self.skill_clusters[f"component_{i + 1}"] = cluster

            return clusters

    def get_skill_recommendations(
        self, skill_name: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get recommendations for related skills based on context."""

        recommendations = {"dependencies": [], "compatible": [], "alternatives": [], "extensions": [], "sequences": []}

        # Get all relationships
        relationships = self.get_relationships(skill_name)

        for relationship in relationships:
            rec = {
                "skill": relationship.target_skill,
                "strength": relationship.strength.value,
                "description": relationship.description,
                "reason": self._get_recommendation_reason(relationship, context),
            }

            # Categorize by relationship type
            if relationship.relationship_type == RelationshipType.DEPENDENCY:
                recommendations["dependencies"].append(rec)
            elif relationship.relationship_type == RelationshipType.COMPATIBLE:
                recommendations["compatible"].append(rec)
            elif relationship.relationship_type == RelationshipType.ALTERNATIVE:
                recommendations["alternatives"].append(rec)
            elif relationship.relationship_type == RelationshipType.EXTENSION:
                recommendations["extensions"].append(rec)
            elif relationship.relationship_type == RelationshipType.SEQUENCE:
                recommendations["sequences"].append(rec)

        # Sort by strength
        for category in recommendations:
            recommendations[category].sort(key=lambda x: x["strength"], reverse=True)

        return recommendations

    def validate_references(self, skill_names: List[str], strict_mode: bool = True) -> ReferenceValidationResult:
        """Validate cross-references for a set of skills."""

        broken_references = []
        circular_dependencies = []
        missing_relationships = []
        suggestions = []

        # Check for broken references
        for skill_name in skill_names:
            relationships = self.get_relationships(skill_name)

            for relationship in relationships:
                if relationship.target_skill not in skill_names:
                    broken_references.append(
                        f"{skill_name} -> {relationship.target_skill} ({relationship.relationship_type.value})"
                    )

        # Check for circular dependencies
        try:
            cycles = list(nx.simple_cycles(self.relationship_graph))

            subgraph_nodes = set(skill_names)
            for cycle in cycles:
                if set(cycle).issubset(subgraph_nodes):
                    circular_dependencies.append(cycle)

        except:
            pass  # NetworkX might fail on some graphs

        # Check for potentially missing relationships
        for skill_name in skill_names:
            # Skills with similar names might have missing relationships
            for other_skill in skill_names:
                if skill_name != other_skill:
                    similarity = self._calculate_name_similarity(skill_name, other_skill)

                    if similarity > 0.8 and not self._has_relationship(skill_name, other_skill):
                        missing_relationships.append(
                            f"Potential missing relationship between {skill_name} and {other_skill} (similarity: {similarity:.2f})"
                        )
                        suggestions.append(
                            f"Consider adding COMPATIBLE or ALTERNATIVE relationship between {skill_name} and {other_skill}"
                        )

        is_valid = len(broken_references) == 0 and (not strict_mode or len(circular_dependencies) == 0)

        return ReferenceValidationResult(
            is_valid=is_valid,
            broken_references=broken_references,
            circular_dependencies=circular_dependencies,
            missing_relationships=missing_relationships,
            suggestions=suggestions,
            relationship_graph=self.relationship_graph.copy(),
        )

    def generate_documentation_cross_references(self, skill_name: str, documentation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cross-reference sections for skill documentation."""

        related_skills = self.get_related_skills(skill_name, max_depth=2)
        recommendations = self.get_skill_recommendations(skill_name)

        # Generate cross-reference content
        cross_refs = {"related_skills": {}, "skill_chains": {}, "clusters": {}, "recommendations": recommendations}

        # Process related skills by relationship type
        for related_skill, relationships in related_skills.items():
            if related_skill == skill_name:
                continue

            # Group by relationship type
            type_groups = defaultdict(list)
            for rel in relationships:
                type_groups[rel.relationship_type.value].append(
                    {"description": rel.description, "strength": rel.strength.value, "bidirectional": rel.bidirectional}
                )

            cross_refs["related_skills"][related_skill] = dict(type_groups)

        # Find common skill chains
        important_skills = [
            skill for skill in related_skills.keys() if any(r.strength.value >= 3 for r in related_skills[skill])
        ]

        for target_skill in important_skills[:5]:  # Limit to top 5
            chains = self.find_skill_chains(skill_name, target_skill, max_length=3)
            if chains:
                cross_refs["skill_chains"][target_skill] = chains[:3]  # Top 3 chains

        # Include cluster information
        for cluster_name, cluster in self.skill_clusters.items():
            if skill_name in cluster.skills:
                cross_refs["clusters"][cluster_name] = {
                    "description": cluster.description,
                    "size": len(cluster.skills),
                    "other_skills": list(cluster.skills - {skill_name})[:5],  # Limit display
                    "common_patterns": cluster.common_patterns,
                    "typical_use_cases": cluster.typical_use_cases,
                }

        return cross_refs

    def _validate_skill_names(self, *skill_names: str) -> None:
        """Validate that skill names are properly formatted."""
        for name in skill_names:
            if not name or not isinstance(name, str):
                raise ValueError(f"Invalid skill name: {name}")

            if not name.replace("_", "").replace("-", "").isalnum():
                raise ValueError(f"Skill name contains invalid characters: {name}")

    def _analyze_cluster_patterns(self, skills: Set[str]) -> List[str]:
        """Analyze common patterns in a skill cluster."""
        patterns = []

        # Look for common prefixes/suffixes
        name_parts = defaultdict(int)
        for skill in skills:
            parts = skill.lower().split("_")
            for part in parts:
                if len(part) > 2:  # Ignore short parts
                    name_parts[part] += 1

        # Find common parts (appear in at least 30% of skills)
        threshold = max(1, len(skills) * 0.3)
        common_parts = [part for part, count in name_parts.items() if count >= threshold]

        for part in common_parts[:3]:  # Limit to top 3
            patterns.append(f"Common pattern: '{part}' ({name_parts[part]} skills)")

        return patterns

    def _analyze_cluster_use_cases(self, skills: Set[str]) -> List[str]:
        """Analyze typical use cases for a skill cluster."""
        use_cases = []

        # Simple heuristic based on skill names
        skills_lower = [s.lower() for s in skills]

        if any("process" in skill or "transform" in skill for skill in skills_lower):
            use_cases.append("Data processing and transformation workflows")

        if any("analyze" in skill or "inspect" in skill for skill in skills_lower):
            use_cases.append("Code analysis and inspection tasks")

        if any("generate" in skill or "create" in skill for skill in skills_lower):
            use_cases.append("Code generation and creation tasks")

        if any("optimize" in skill or "improve" in skill for skill in skills_lower):
            use_cases.append("Performance optimization and improvement")

        return use_cases[:3]  # Limit to top 3

    def _get_recommendation_reason(self, relationship: SkillRelationship, context: Optional[Dict[str, Any]]) -> str:
        """Get a human-readable reason for a recommendation."""

        base_reason = relationship.description or f"{relationship.relationship_type.value} relationship"

        if context:
            # Context-aware reasoning
            if context.get("task_type") == "optimization":
                if relationship.relationship_type == RelationshipType.ALTERNATIVE:
                    return f"{base_reason} - alternative approach for optimization"
                elif relationship.relationship_type == RelationshipType.COMPATIBLE:
                    return f"{base_reason} - can enhance optimization workflow"

            if context.get("complexity") == "high":
                if relationship.strength.value >= 3:
                    return f"{base_reason} - recommended for complex tasks"

        return base_reason

    def _has_relationship(self, skill1: str, skill2: str) -> bool:
        """Check if any relationship exists between two skills."""

        for relationship in self.relationships.get(skill1, []):
            if relationship.target_skill == skill2:
                return True

        for relationship in self.reverse_relationships.get(skill1, []):
            if relationship.source_skill == skill2:
                return True

        return False

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two skill names."""

        # Simple similarity based on common parts
        parts1 = set(name1.lower().split("_"))
        parts2 = set(name2.lower().split("_"))

        if not parts1 or not parts2:
            return 0.0

        intersection = parts1.intersection(parts2)
        union = parts1.union(parts2)

        return len(intersection) / len(union)

    def _load_relationships(self) -> None:
        """Load relationships from storage."""

        relationships_file = self.storage_path / "relationships.json"

        if relationships_file.exists():
            try:
                with open(relationships_file, "r") as f:
                    data = json.load(f)

                for rel_data in data.get("relationships", []):
                    relationship = SkillRelationship(
                        source_skill=rel_data["source_skill"],
                        target_skill=rel_data["target_skill"],
                        relationship_type=RelationshipType(rel_data["relationship_type"]),
                        strength=RelationshipStrength(rel_data["strength"]),
                        description=rel_data.get("description", ""),
                        bidirectional=rel_data.get("bidirectional", False),
                        metadata=rel_data.get("metadata", {}),
                    )

                    self.add_relationship(relationship)

                # Load clusters
                for cluster_data in data.get("clusters", []):
                    cluster = SkillCluster(
                        name=cluster_data["name"],
                        skills=set(cluster_data["skills"]),
                        description=cluster_data.get("description", ""),
                        common_patterns=cluster_data.get("common_patterns", []),
                        typical_use_cases=cluster_data.get("typical_use_cases", []),
                    )

                    self.skill_clusters[cluster.name] = cluster

            except Exception as e:
                print(f"Error loading relationships: {e}")

    def save_relationships(self) -> None:
        """Save relationships to storage."""

        # Flatten relationships for storage
        all_relationships = []
        seen_relationships = set()  # Avoid duplicates

        for relationships in self.relationships.values():
            for relationship in relationships:
                # Create unique identifier
                rel_id = (relationship.source_skill, relationship.target_skill, relationship.relationship_type.value)

                if rel_id not in seen_relationships:
                    all_relationships.append(
                        {
                            "source_skill": relationship.source_skill,
                            "target_skill": relationship.target_skill,
                            "relationship_type": relationship.relationship_type.value,
                            "strength": relationship.strength.value,
                            "description": relationship.description,
                            "bidirectional": relationship.bidirectional,
                            "metadata": relationship.metadata,
                        }
                    )

                    seen_relationships.add(rel_id)

        # Prepare clusters data
        clusters_data = []
        for cluster in self.skill_clusters.values():
            clusters_data.append(
                {
                    "name": cluster.name,
                    "skills": list(cluster.skills),
                    "description": cluster.description,
                    "common_patterns": cluster.common_patterns,
                    "typical_use_cases": cluster.typical_use_cases,
                }
            )

        # Save to file
        data = {
            "relationships": all_relationships,
            "clusters": clusters_data,
            "metadata": {
                "total_relationships": len(all_relationships),
                "total_clusters": len(clusters_data),
                "last_updated": str(Path().resolve()),  # Simple timestamp
            },
        }

        with open(self.storage_path / "relationships.json", "w") as f:
            json.dump(data, f, indent=2)

    def export_relationship_graph(self, format: str = "graphml") -> str:
        """Export the relationship graph in specified format."""

        output_path = self.storage_path / f"skill_relationships.{format}"

        if format == "graphml":
            nx.write_graphml(self.relationship_graph, output_path)
        elif format == "gexf":
            nx.write_gexf(self.relationship_graph, output_path)
        elif format == "json":
            data = nx.node_link_data(self.relationship_graph)
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return str(output_path)

    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get statistics about the relationship network."""

        stats = {
            "total_skills": len(self.relationship_graph.nodes),
            "total_relationships": len(self.relationship_graph.edges),
            "relationship_types": defaultdict(int),
            "relationship_strengths": defaultdict(int),
            "connected_components": 0,
            "average_degree": 0.0,
            "clustering_coefficient": 0.0,
        }

        # Count relationship types and strengths
        for _, _, edge_data in self.relationship_graph.edges(data=True):
            rel_type = edge_data.get("relationship_type", "unknown")
            strength = edge_data.get("strength", 1)

            stats["relationship_types"][rel_type] += 1
            stats["relationship_strengths"][strength] += 1

        # Graph metrics
        if len(self.relationship_graph.nodes) > 0:
            stats["connected_components"] = nx.number_connected_components(self.relationship_graph.to_undirected())
            stats["average_degree"] = sum(dict(self.relationship_graph.degree()).values()) / len(
                self.relationship_graph.nodes
            )

            try:
                stats["clustering_coefficient"] = nx.average_clustering(self.relationship_graph.to_undirected())
            except:
                stats["clustering_coefficient"] = 0.0

        return dict(stats)
