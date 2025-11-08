#!/usr/bin/env python3
"""
UI Rapid Prototyping Assistant: Powered by CreaTech

A specialized agent for rapid UI prototyping and workflow design,
specifically tailored for complex scheduling applications like PumpTracker.
Combines creative design with technical implementation intelligence.
"""

import argparse
import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Import CreaTech components
from main_assistant import CreaTechAssistant

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class UIRapidPrototyper:
    """UI Rapid Prototyping Assistant powered by CreaTech"""

    def __init__(self):
        self.crean_assistant = CreaTechAssistant()
        self.workspace = Path("ui_prototyping_workspace")
        self.workspace.mkdir(exist_ok=True)

        # Load PumpTracker context
        self.pumptracker_data = self._load_pumptracker_data()
        self.prototyping_history = []

        logger.info("🎨 UI Rapid Prototyping Assistant initialized")
        logger.info(f"📊 Loaded {len(self.pumptracker_data.get('models', []))} pump models")
        logger.info(f"👥 Loaded {len(self.pumptracker_data.get('customers', []))} customers")

    def _load_pumptracker_data(self) -> dict[str, Any]:
        """Load PumpTracker data for context"""
        try:
            data_file = Path(
                "/home/markimus/projects/microsoft-amplifier/pumptracker-manus/src/data/pumptracker-data.json"
            )
            if data_file.exists():
                with open(data_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load PumpTracker data: {e}")

        # Fallback data
        return {
            "models": [
                {
                    "model": "DD-4S",
                    "description": '4" Double Diaphragm',
                    "price": 20000,
                    "lead_times": {"total_days": 9.75},
                },
                {
                    "model": "DD-6",
                    "description": '6" Double Diaphragm',
                    "price": 24000,
                    "lead_times": {"total_days": 9.75},
                },
                {"model": "RL200", "description": '8" Rotary Lobe', "price": 45000, "lead_times": {"total_days": 9.75}},
            ],
            "customers": ["United Rentals", "Sunbelt Rentals", "Herc Rentals"],
            "productionStages": ["Not Started", "Fabrication", "Powder Coat", "Assembly", "Testing", "Shipping"],
        }

    async def analyze_ui_requirements(self, user_description: str, context: dict | None = None) -> dict[str, Any]:
        """Analyze UI requirements using CreaTech's creative-technical intelligence"""

        logger.info(f"🔍 Analyzing UI requirements: {user_description}")

        # Use CreaTech for requirement analysis
        analysis = await self.crean_assistant.analyze_requirement(user_description)

        # Add UI-specific analysis
        ui_analysis = {
            "user_description": user_description,
            "domain_analysis": analysis,
            "ui_challenges": self._identify_ui_challenges(user_description),
            "technical_considerations": self._identify_technical_considerations(user_description),
            "design_opportunities": self._identify_design_opportunities(user_description),
            "user_workflow_complexity": self._assess_workflow_complexity(user_description),
            "prototyping_priority": self._determine_prototyping_priority(user_description),
        }

        return ui_analysis

    def _identify_ui_challenges(self, description: str) -> list[str]:
        """Identify specific UI challenges based on description"""
        challenges = []
        desc_lower = description.lower()

        if "drag" in desc_lower or "drop" in desc_lower:
            challenges.append("drag_drop_implementation")
        if "calendar" in desc_lower or "schedule" in desc_lower:
            challenges.append("calendar_integration")
        if "pump" in desc_lower or "manufacturing" in desc_lower:
            challenges.append("industrial_workflow_optimization")
        if "card" in desc_lower:
            challenges.append("card_based_interface")
        if "job" in desc_lower or "production" in desc_lower:
            challenges.append("production_status_visualization")
        if "complex" in desc_lower or "many" in desc_lower:
            challenges.append("information_density_management")

        return challenges if challenges else ["general_ui_optimization"]

    def _identify_technical_considerations(self, description: str) -> list[str]:
        """Identify technical implementation considerations"""
        considerations = []
        desc_lower = description.lower()

        if "drag" in desc_lower or "drop" in desc_lower:
            considerations.extend(["drag_drop_library", "touch_interface_support"])
        if "calendar" in desc_lower:
            considerations.extend(["calendar_library", "date_handling", "timezone_support"])
        if "schedule" in desc_lower:
            considerations.extend(["state_management", "real_time_updates", "conflict_detection"])
        if "responsive" in desc_lower:
            considerations.append("responsive_design")

        return considerations if considerations else ["modern_ui_framework"]

    def _identify_design_opportunities(self, description: str) -> list[str]:
        """Identify creative design opportunities"""
        opportunities = []
        desc_lower = description.lower()

        if "simple" in desc_lower or "intuitive" in desc_lower:
            opportunities.append("minimalist_design")
        if "visual" in desc_lower or "beautiful" in desc_lower:
            opportunities.append("enhanced_visual_appeal")
        if "quick" in desc_lower or "fast" in desc_lower:
            opportunities.append("performance_optimization")
        if "mobile" in desc_lower:
            opportunities.append("mobile_first_design")

        opportunities.extend(["innovative_interaction_patterns", "delightful_micro_interactions"])
        return opportunities

    def _assess_workflow_complexity(self, description: str) -> str:
        """Assess the complexity of the user workflow"""
        desc_lower = description.lower()

        complexity_indicators = {
            "high": ["complex", "many factors", "multiple", "advanced", "sophisticated"],
            "medium": ["schedule", "manage", "organize", "track"],
            "low": ["simple", "basic", "straightforward"],
        }

        for level, indicators in complexity_indicators.items():
            if any(indicator in desc_lower for indicator in indicators):
                return level

        return "medium"

    def _determine_prototyping_priority(self, description: str) -> list[str]:
        """Determine prototyping priorities based on user concerns"""
        desc_lower = description.lower()
        priorities = []

        if "confuse" in desc_lower or "overwhelm" in desc_lower:
            priorities.append("usability_clarity")
        if "derail" in desc_lower or "catastrophe" in desc_lower:
            priorities.append("risk_mitigation")
        if "iterate" in desc_lower or "quick" in desc_lower:
            priorities.append("rapid_iteration")
        if "simple" in desc_lower:
            priorities.append("workflow_simplification")

        priorities.extend(["user_experience", "visual_design", "technical_feasibility"])
        return priorities

    async def generate_ui_concepts(self, analysis: dict[str, Any], num_concepts: int = 3) -> list[dict[str, Any]]:
        """Generate multiple UI concepts using CreaTech's creative intelligence"""

        logger.info(f"💡 Generating {num_concepts} UI concepts...")

        concepts = []

        # Generate base concepts using CreaTech
        base_concepts = await self.crean_assistant.generate_creative_concepts(analysis["domain_analysis"])

        for i in range(min(num_concepts, len(base_concepts))):
            base_concept = base_concepts[i]

            # Transform into UI-specific concept
            ui_concept = {
                "concept_id": str(uuid.uuid4())[:8],
                "concept_name": f"UI Concept {i + 1}: {base_concept['concept_name']}",
                "design_approach": base_concept["pattern_type"],
                "key_features": self._generate_ui_features(base_concept, analysis),
                "interaction_patterns": self._generate_interaction_patterns(base_concept, analysis),
                "visual_style": self._generate_visual_style(base_concept, analysis),
                "technical_approach": self._generate_technical_approach(base_concept, analysis),
                "user_benefits": self._generate_user_benefits(base_concept, analysis),
                "prototype_complexity": self._assess_prototype_complexity(base_concept, analysis),
                "estimated_development_time": self._estimate_development_time(base_concept, analysis),
                "confidence_score": base_concept["estimated_impact"],
            }

            concepts.append(ui_concept)

        logger.info(f"✅ Generated {len(concepts)} UI concepts")
        return concepts

    def _generate_ui_features(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """Generate specific UI features based on concept and analysis"""
        features = []

        # Base features from challenges
        for challenge in analysis["ui_challenges"]:
            if challenge == "drag_drop_implementation":
                features.extend(["Drag & drop pump cards", "Visual drag feedback", "Drop zone indicators"])
            elif challenge == "calendar_integration":
                features.extend(["Calendar view", "Date picker", "Schedule timeline"])
            elif challenge == "production_status_visualization":
                features.extend(["Status indicators", "Progress bars", "Stage tracking"])

        # Add creative elements from concept
        if concept["pattern_type"] == "design_thinking":
            features.extend(["User-centered workflow", "Intuitive navigation", "Clear visual hierarchy"])
        elif concept["pattern_type"] == "generative_art":
            features.extend(["Dynamic visualizations", "Animated transitions", "Responsive layouts"])

        return features

    def _generate_interaction_patterns(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """Generate interaction patterns for the UI"""
        patterns = []

        if "drag_drop_implementation" in analysis["ui_challenges"]:
            patterns.extend(["Touch-friendly drag controls", "Hover state feedback", "Keyboard navigation support"])

        if "calendar_integration" in analysis["ui_challenges"]:
            patterns.extend(["Click to schedule", "Drag to reschedule", "Multi-select for bulk actions"])

        # Add concept-specific patterns
        if concept["pattern_type"] == "creative_coding":
            patterns.extend(["Gesture-based interactions", "Contextual menus", "Keyboard shortcuts"])

        return patterns

    def _generate_visual_style(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Generate visual style recommendations"""
        base_style = {
            "color_palette": "Professional industrial theme",
            "typography": "Clean, readable sans-serif",
            "spacing": "Generous white space for clarity",
            "iconography": "Intuitive icon set",
        }

        if concept["pattern_type"] == "design_thinking":
            base_style.update(
                {
                    "primary_colors": ["#2563eb", "#7c3aed", "#dc2626"],  # Professional blues/purples
                    "design_language": "Modern, clean, user-friendly",
                }
            )
        elif concept["pattern_type"] == "generative_art":
            base_style.update(
                {
                    "primary_colors": ["#0891b2", "#059669", "#7c2d12"],  # Cyan/green/brown industrial
                    "design_language": "Dynamic, engaging, innovative",
                }
            )

        return base_style

    def _generate_technical_approach(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """Generate technical implementation approach"""
        approach = ["Modern web framework", "Component-based architecture", "State management"]

        if "drag_drop_implementation" in analysis["ui_challenges"]:
            approach.extend(["Drag & drop library integration", "Touch event handling"])

        if "calendar_integration" in analysis["ui_challenges"]:
            approach.extend(["Calendar component library", "Date manipulation utilities"])

        if concept["pattern_type"] == "creative_coding":
            approach.extend(["Custom animation library", "Canvas/WebGL for visualizations"])

        return approach

    def _generate_user_benefits(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """Generate user benefits of the concept"""
        benefits = ["Reduced scheduling complexity", "Visual workflow clarity", "Faster decision making"]

        if analysis["user_workflow_complexity"] == "high":
            benefits.extend(["Simplified complex workflows", "Reduced cognitive load"])

        if "usability_clarity" in analysis["prototyping_priority"]:
            benefits.extend(["Intuitive interface", "Minimal learning curve"])

        return benefits

    def _assess_prototype_complexity(self, concept: dict[str, Any], analysis: dict[str, Any]) -> str:
        """Assess the complexity of building this prototype"""
        complexity_score = 0

        # Score based on challenges
        for challenge in analysis["ui_challenges"]:
            if challenge == "drag_drop_implementation":
                complexity_score += 2
            elif challenge == "calendar_integration" or challenge == "production_status_visualization":
                complexity_score += 1

        # Adjust based on concept complexity
        if concept["estimated_impact"] > 0.8:
            complexity_score += 1

        if complexity_score <= 2:
            return "Low"
        if complexity_score <= 4:
            return "Medium"
        return "High"

    def _estimate_development_time(self, concept: dict[str, Any], analysis: dict[str, Any]) -> str:
        """Estimate development time for the prototype"""
        complexity = self._assess_prototype_complexity(concept, analysis)

        time_estimates = {"Low": "1-2 days", "Medium": "3-5 days", "High": "1-2 weeks"}

        return time_estimates.get(complexity, "3-5 days")

    async def create_prototype_specification(
        self, selected_concept: dict[str, Any], analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Create detailed prototype specification"""

        logger.info(f"📋 Creating prototype specification for: {selected_concept['concept_name']}")

        # Use CreaTech synthesis for technical integration
        synthesis_prompt = f"""
        Create a detailed prototype specification for a pump scheduling UI with:
        - Design approach: {selected_concept["design_approach"]}
        - Key features: {", ".join(selected_concept["key_features"])}
        - Interaction patterns: {", ".join(selected_concept["interaction_patterns"])}
        - Visual style: {selected_concept["visual_style"]["design_language"]}
        - Technical approach: {", ".join(selected_concept["technical_approach"])}
        """

        synthesis_result = await self.crean_assistant.synthesize_solution(synthesis_prompt)

        # Build comprehensive specification
        specification = {
            "prototype_id": f"PT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "concept_summary": selected_concept,
            "technical_specification": {
                "framework_recommendations": synthesis_result.synthesized_solution.get("technical_core", []),
                "component_structure": self._design_component_structure(selected_concept, analysis),
                "data_flow": self._design_data_flow(selected_concept, analysis),
                "state_management": self._design_state_management(selected_concept, analysis),
            },
            "ui_specification": {
                "layout_design": self._design_layout(selected_concept, analysis),
                "component_details": self._design_components(selected_concept, analysis),
                "interaction_details": self._design_interactions(selected_concept, analysis),
                "responsive_behavior": self._design_responsive_behavior(selected_concept, analysis),
            },
            "implementation_plan": {
                "development_phases": self._plan_development_phases(selected_concept, analysis),
                "mock_data_strategy": self._plan_mock_data(selected_concept, analysis),
                "testing_approach": self._plan_testing_approach(selected_concept, analysis),
                "success_metrics": self._define_success_metrics(selected_concept, analysis),
            },
            "next_steps": self._generate_next_steps(selected_concept, analysis),
            "confidence_assessment": {
                "technical_feasibility": synthesis_result.feasibility_score,
                "user_experience_quality": synthesis_result.aesthetic_score,
                "implementation_confidence": synthesis_result.confidence_score,
            },
        }

        return specification

    def _design_component_structure(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, list[str]]:
        """Design the component structure"""
        structure = {
            "layout_components": ["App", "Header", "MainContent", "Sidebar"],
            "scheduling_components": ["Calendar", "ScheduleTimeline", "DragDropArea"],
            "pump_components": ["PumpCard", "PumpDetails", "StatusIndicator"],
            "utility_components": ["DatePicker", "FilterControls", "StatusBar"],
        }

        if "drag_drop_implementation" in analysis["ui_challenges"]:
            structure["interaction_components"] = ["DragHandle", "DropZone", "DragPreview"]

        return structure

    def _design_data_flow(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Design the data flow architecture"""
        return {
            "data_sources": ["PumpTracker API", "User Preferences", "Schedule State"],
            "state_management": ["Schedule State", "UI State", "Filter State"],
            "data_transformations": ["Schedule Optimization", "Conflict Detection", "Status Updates"],
            "real_time_updates": ["Schedule Changes", "Status Updates", "User Actions"],
        }

    def _design_state_management(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Design state management approach"""
        return {
            "global_state": ["Current Schedule", "Selected Pumps", "Filter Settings"],
            "component_state": ["Drag State", "Calendar View", "Expanded Items"],
            "persistent_state": ["User Preferences", "Schedule History"],
            "state_updates": ["User Actions", "System Updates", "Real-time Synchronization"],
        }

    def _design_layout(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Design the layout structure"""
        layout = {
            "overall_structure": "Responsive grid layout",
            "header": ["App title", "User controls", "Help button"],
            "main_area": {
                "left_panel": ["Calendar view", "Mini timeline"],
                "center_panel": ["Main scheduling area", "Drag & drop zones"],
                "right_panel": ["Pump details", "Schedule summary"],
            },
            "footer": ["Status bar", "Quick actions", "Progress indicators"],
        }

        if analysis["user_workflow_complexity"] == "high":
            layout["main_area"]["additional_panels"] = ["Advanced filters", "Bulk actions"]

        return layout

    def _design_components(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Design detailed component specifications"""
        components = {
            "PumpCard": {
                "purpose": "Display pump information in draggable format",
                "content": ["Model name", "Customer", "Status", "Deadline"],
                "interactions": ["Drag to schedule", "Click for details", "Right-click menu"],
                "styling": "Card-based design with status color coding",
            },
            "Calendar": {
                "purpose": "Display production calendar",
                "content": ["Monthly/weekly view", "Production capacity", "Scheduled items"],
                "interactions": ["Navigate dates", "Click to add items", "Drag items onto"],
                "styling": "Clean calendar with capacity indicators",
            },
        }

        if "drag_drop_implementation" in analysis["ui_challenges"]:
            components["DragDropArea"] = {
                "purpose": "Handle drag and drop scheduling",
                "content": ["Drop zones", "Visual feedback", "Conflict warnings"],
                "interactions": ["Drag enter/leave events", "Drop validation", "Undo/redo"],
                "styling": "Clear visual indicators for drop zones",
            }

        return components

    def _design_interactions(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Design interaction patterns"""
        interactions = {
            "primary_interactions": ["Drag pump to schedule", "Click to view details", "Navigate calendar"],
            "keyboard_shortcuts": ["Escape to cancel", "Delete to remove", "Ctrl+Z to undo"],
            "touch_gestures": ["Swipe to navigate", "Tap to select", "Long press for menu"],
            "visual_feedback": ["Hover states", "Drag previews", "Success/error indicators"],
        }

        return interactions

    def _design_responsive_behavior(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Design responsive behavior"""
        return {
            "desktop_layout": "Full three-panel layout",
            "tablet_layout": "Collapsible sidebars, stacked main content",
            "mobile_layout": "Single column with tab navigation",
            "breakpoints": ["768px", "1024px", "1440px"],
        }

    def _plan_development_phases(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """Plan development phases"""
        phases = [
            {
                "phase": "Phase 1: Core Structure",
                "duration": "1-2 days",
                "deliverables": ["Basic layout", "Component structure", "Mock data integration"],
                "success_criteria": ["Layout renders correctly", "Components display data"],
            },
            {
                "phase": "Phase 2: Interactions",
                "duration": "1-2 days",
                "deliverables": ["Drag & drop functionality", "Calendar navigation", "Basic state management"],
                "success_criteria": ["Can drag pumps to schedule", "Calendar navigation works"],
            },
            {
                "phase": "Phase 3: Polish & Refinement",
                "duration": "1 day",
                "deliverables": ["Visual styling", "Animations", "Error handling"],
                "success_criteria": ["Professional appearance", "Smooth interactions"],
            },
        ]

        return phases

    def _plan_mock_data(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan mock data strategy"""
        return {
            "data_sources": ["PumpTracker catalog", "Sample schedules", "User scenarios"],
            "data_structure": {
                "pumps": ["Model info", "Customer", "Production requirements", "Timeline"],
                "schedule": ["Dates", "Capacity", "Conflicts", "Dependencies"],
                "users": ["Preferences", "Permissions", "History"],
            },
            "generation_strategy": "Use existing PumpTracker data with realistic scheduling scenarios",
        }

    def _plan_testing_approach(self, concept: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan testing approach"""
        return {
            "user_testing": ["Workflow completion tasks", "Ease of use feedback", "Preference gathering"],
            "technical_testing": ["Drag & drop reliability", "Performance under load", "Cross-browser compatibility"],
            "iteration_cycles": ["Rapid prototype cycles", "User feedback integration", "Continuous refinement"],
        }

    def _define_success_metrics(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """Define success metrics"""
        return [
            "Users can schedule a pump in under 30 seconds",
            "No confusion about production capacity",
            "Positive feedback on visual design",
            "Intuitive drag & drop interaction",
            "Clear understanding of schedule conflicts",
        ]

    def _generate_next_steps(self, concept: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
        """Generate next steps for implementation"""
        steps = [
            "Create HTML/CSS prototype with basic styling",
            "Implement drag & drop functionality",
            "Integrate PumpTracker data model",
            "Set up user testing session",
            "Iterate based on feedback",
        ]

        if analysis["user_workflow_complexity"] == "high":
            steps.insert(0, "Simplify workflow complexity before prototyping")

        return steps

    async def generate_html_prototype(self, specification: dict[str, Any]) -> str:
        """Generate HTML prototype based on specification"""

        logger.info("🌐 Generating HTML prototype...")

        # Use CreaTech web application workflow
        web_requirement = f"""
        Create a pump scheduling UI prototype with:
        - Visual style: {specification["concept_summary"]["visual_style"]["design_language"]}
        - Key features: {", ".join(specification["concept_summary"]["key_features"][:3])}
        - Layout: Responsive design with calendar and drag-drop scheduling
        - Color scheme: Professional industrial theme
        - Mock data: Use PumpTracker catalog data
        """

        web_result = await self.crean_assistant.run_creative_web_application_workflow(
            web_requirement,
            design_preferences={
                "visual_style": specification["concept_summary"]["visual_style"]["design_language"],
                "user_experience": "delightful_interactions",
                "accessibility": "high_priority",
            },
        )

        # Generate HTML prototype
        html_content = self._build_html_prototype(specification, web_result)

        # Save prototype
        prototype_file = self.workspace / f"prototype-{specification['prototype_id']}.html"
        with open(prototype_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"✅ HTML prototype saved to {prototype_file}")
        return str(prototype_file)

    def _build_html_prototype(self, specification: dict[str, Any], web_result: dict[str, Any]) -> str:
        """Build the HTML prototype content"""

        concept = specification["concept_summary"]
        visual_style = concept["visual_style"]

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PumpTracker Scheduling UI Prototype</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary-color: {self._get_primary_color(visual_style)};
            --secondary-color: {self._get_secondary_color(visual_style)};
            --accent-color: {self._get_accent_color(visual_style)};
            --background-color: #f8fafc;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .main-content {{
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}

        .panel {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
        }}

        .panel h2 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--primary-color);
        }}

        .pump-card {{
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: move;
            transition: all 0.2s ease;
            position: relative;
        }}

        .pump-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-color: var(--accent-color);
        }}

        .pump-card.dragging {{
            opacity: 0.5;
            transform: rotate(2deg);
        }}

        .pump-model {{
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--primary-color);
            margin-bottom: 4px;
        }}

        .pump-description {{
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }}

        .pump-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}

        .customer {{
            background: var(--accent-color);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 500;
        }}

        .timeline {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border: 2px dashed var(--border-color);
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            transition: all 0.2s ease;
        }}

        .timeline.drag-over {{
            border-color: var(--primary-color);
            background: rgba(37, 99, 235, 0.05);
            color: var(--primary-color);
        }}

        .timeline.scheduled {{
            border-style: solid;
            border-color: var(--success-color);
            background: rgba(16, 185, 129, 0.05);
            color: var(--text-color);
        }}

        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }}

        .status-not-started {{ background: #94a3b8; }}
        .status-fabrication {{ background: var(--primary-color); }}
        .status-assembly {{ background: var(--warning-color); }}
        .status-shipping {{ background: var(--success-color); }}

        .calendar {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
            background: var(--border-color);
            padding: 2px;
            border-radius: 8px;
        }}

        .calendar-day {{
            background: white;
            padding: 8px;
            text-align: center;
            font-size: 0.85rem;
            min-height: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
        }}

        .calendar-day.today {{
            background: var(--accent-color);
            color: white;
            font-weight: 600;
        }}

        .calendar-day.has-jobs {{
            background: linear-gradient(135deg, white, rgba(37, 99, 235, 0.1));
            border: 1px solid var(--primary-color);
        }}

        .drop-zone {{
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            color: #94a3b8;
            transition: all 0.2s ease;
            margin: 12px 0;
        }}

        .drop-zone.active {{
            border-color: var(--primary-color);
            background: rgba(37, 99, 235, 0.05);
            color: var(--primary-color);
        }}

        .prototype-info {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}

        .prototype-info h3 {{
            margin-bottom: 8px;
            font-size: 1.25rem;
        }}

        .confidence-badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            margin-top: 8px;
        }}

        @media (max-width: 1024px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}

            .panel {{
                margin-bottom: 16px;
            }}
        }}

        .drag-handle {{
            position: absolute;
            top: 8px;
            right: 8px;
            cursor: move;
            color: #94a3b8;
            font-size: 12px;
        }}

        .scheduled-item {{
            background: var(--primary-color);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            margin: 2px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 PumpTracker Scheduling UI</h1>
            <p>Drag & Drop Pump Production Scheduling Prototype</p>
        </div>

        <div class="main-content">
            <!-- Left Panel: Available Pumps -->
            <div class="panel">
                <h2>📦 Available Pumps</h2>
                <div id="pump-list">
                    {self._generate_pump_cards()}
                </div>
            </div>

            <!-- Center Panel: Scheduling Area -->
            <div class="panel">
                <h2>📅 Production Schedule</h2>
                <div id="schedule-area">
                    {self._generate_schedule_timeline()}
                </div>

                <h3 style="margin-top: 24px;">📆 Calendar View</h3>
                <div class="calendar" id="calendar">
                    {self._generate_calendar()}
                </div>
            </div>

            <!-- Right Panel: Schedule Details -->
            <div class="panel">
                <h2>📊 Schedule Overview</h2>
                <div id="schedule-summary">
                    <div style="margin-bottom: 16px;">
                        <strong>Total Scheduled:</strong> <span id="scheduled-count">0</span> pumps
                    </div>
                    <div style="margin-bottom: 16px;">
                        <strong>Production Capacity:</strong> 3 pumps/day
                    </div>
                    <div style="margin-bottom: 16px;">
                        <strong>Next Available:</strong> Tomorrow
                    </div>
                </div>

                <h3>🎯 Quick Actions</h3>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button onclick="clearSchedule()" style="padding: 8px 16px; background: var(--error-color); color: white; border: none; border-radius: 6px; cursor: pointer;">
                        Clear Schedule
                    </button>
                    <button onclick="autoSchedule()" style="padding: 8px 16px; background: var(--success-color); color: white; border: none; border-radius: 6px; cursor: pointer;">
                        Auto Schedule
                    </button>
                    <button onclick="exportSchedule()" style="padding: 8px 16px; background: var(--primary-color); color: white; border: none; border-radius: 6px; cursor: pointer;">
                        Export Schedule
                    </button>
                </div>
            </div>
        </div>

        <div class="prototype-info">
            <h3>🎨 {concept["concept_name"]}</h3>
            <p>UI Rapid Prototyping Assistant - CreaTech Powered</p>
            <div class="confidence-badge">
                Confidence: {concept["confidence_score"]:.1%} |
                Complexity: {concept["prototype_complexity"]} |
                Est. Time: {concept["estimated_development_time"]}
            </div>
        </div>
    </div>

    <script>
        // Drag and Drop functionality
        let draggedElement = null;
        let scheduledPumps = [];

        document.addEventListener('DOMContentLoaded', function() {{
            initializeDragAndDrop();
            updateScheduleCount();
        }});

        function initializeDragAndDrop() {{
            // Make pump cards draggable
            document.querySelectorAll('.pump-card').forEach(card => {{
                card.draggable = true;
                card.addEventListener('dragstart', handleDragStart);
                card.addEventListener('dragend', handleDragEnd);
            }});

            // Make timelines droppable
            document.querySelectorAll('.timeline').forEach(timeline => {{
                timeline.addEventListener('dragover', handleDragOver);
                timeline.addEventListener('drop', handleDrop);
                timeline.addEventListener('dragleave', handleDragLeave);
            }});
        }}

        function handleDragStart(e) {{
            draggedElement = e.target;
            e.target.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/html', e.target.innerHTML);
        }}

        function handleDragEnd(e) {{
            e.target.classList.remove('dragging');
        }}

        function handleDragOver(e) {{
            if (e.preventDefault) {{
                e.preventDefault();
            }}
            e.dataTransfer.dropEffect = 'move';
            e.target.classList.add('drag-over');
            return false;
        }}

        function handleDragLeave(e) {{
            e.target.classList.remove('drag-over');
        }}

        function handleDrop(e) {{
            if (e.stopPropagation) {{
                e.stopPropagation();
            }}
            e.preventDefault();

            const timeline = e.target.closest('.timeline');
            if (timeline && draggedElement) {{
                timeline.classList.remove('drag-over');
                timeline.classList.add('scheduled');

                // Add scheduled item to timeline
                const pumpInfo = draggedElement.querySelector('.pump-model').textContent;
                const scheduledItem = document.createElement('div');
                scheduledItem.className = 'scheduled-item';
                scheduledItem.textContent = pumpInfo;
                timeline.appendChild(scheduledItem);

                // Hide original pump card
                draggedElement.style.display = 'none';

                // Update scheduled pumps array
                scheduledPumps.push({{
                    model: pumpInfo,
                    timeline: timeline.id
                }});

                updateScheduleCount();
                showSuccessFeedback(timeline);
            }}

            return false;
        }}

        function updateScheduleCount() {{
            document.getElementById('scheduled-count').textContent = scheduledPumps.length;
        }}

        function showSuccessFeedback(element) {{
            element.style.background = 'rgba(16, 185, 129, 0.2)';
            setTimeout(() => {{
                element.style.background = '';
            }}, 1000);
        }}

        function clearSchedule() {{
            if (confirm('Clear all scheduled pumps?')) {{
                document.querySelectorAll('.timeline').forEach(timeline => {{
                    timeline.classList.remove('scheduled');
                    timeline.innerHTML = timeline.id.includes('monday') ? 'Monday - Drop pumps here' :
                                    timeline.id.includes('tuesday') ? 'Tuesday - Drop pumps here' : 'Drop pumps here';
                }});

                document.querySelectorAll('.pump-card').forEach(card => {{
                    card.style.display = '';
                }});

                scheduledPumps = [];
                updateScheduleCount();
            }}
        }}

        function autoSchedule() {{
            const availablePumps = document.querySelectorAll('.pump-card:not([style*="display: none"])');
            const timelines = document.querySelectorAll('.timeline');

            availablePumps.forEach((pump, index) => {{
                setTimeout(() => {{
                    if (index < timelines.length) {{
                        const timeline = timelines[index];
                        const pumpInfo = pump.querySelector('.pump-model').textContent;

                        timeline.classList.add('scheduled');
                        timeline.innerHTML = `<div class="scheduled-item">${{pumpInfo}}</div>`;
                        pump.style.display = 'none';

                        scheduledPumps.push({{
                            model: pumpInfo,
                            timeline: timeline.id
                        }});

                        updateScheduleCount();
                        showSuccessFeedback(timeline);
                    }}
                }}, index * 300);
            }});
        }}

        function exportSchedule() {{
            const scheduleData = {{
                scheduled_pumps: scheduledPumps,
                total_count: scheduledPumps.length,
                export_date: new Date().toISOString()
            }};

            const dataStr = JSON.stringify(scheduleData, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

            const exportFileDefaultName = 'pumptracker-schedule.json';

            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        }}
    </script>
</body>
</html>
        """

        return html_template

    def _get_primary_color(self, visual_style: dict[str, Any]) -> str:
        """Get primary color based on visual style"""
        design_language = visual_style.get("design_language", "").lower()
        if "modern" in design_language or "clean" in design_language:
            return "#2563eb"
        if "dynamic" in design_language or "engaging" in design_language:
            return "#0891b2"
        return "#7c3aed"

    def _get_secondary_color(self, visual_style: dict[str, Any]) -> str:
        """Get secondary color based on visual style"""
        return "#64748b"

    def _get_accent_color(self, visual_style: dict[str, Any]) -> str:
        """Get accent color based on visual style"""
        return "#f59e0b"

    def _generate_pump_cards(self) -> str:
        """Generate HTML for pump cards"""
        pump_cards = []

        for pump in self.pumptracker_data["models"][:6]:  # Show first 6 pumps
            customer = self.pumptracker_data["customers"][hash(pump["model"]) % len(self.pumptracker_data["customers"])]

            card_html = f"""
                <div class="pump-card" draggable="true">
                    <div class="drag-handle">⋮⋮</div>
                    <div class="pump-model">{pump["model"]}</div>
                    <div class="pump-description">{pump["description"]}</div>
                    <div class="pump-meta">
                        <span class="customer">{customer}</span>
                        <span class="status-indicator status-not-started"></span>
                    </div>
                </div>
            """
            pump_cards.append(card_html)

        return "\n".join(pump_cards)

    def _generate_schedule_timeline(self) -> str:
        """Generate HTML for schedule timeline"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        timelines = []

        for day in days:
            timeline_html = f"""
                <div class="timeline" id="timeline-{day.lower()}">
                    {day} - Drop pumps here
                </div>
            """
            timelines.append(timeline_html)

        return "\n".join(timelines)

    def _generate_calendar(self) -> str:
        """Generate HTML for calendar"""
        calendar_days = []

        # Generate a simple 5-week calendar
        for week in range(5):
            for day in range(7):
                day_num = week * 7 + day + 1
                if day_num <= 31:
                    is_today = day_num == 15  # Make 15th "today"
                    has_jobs = day_num in [14, 15, 16, 21, 22]  # Some days have jobs

                    classes = ["calendar-day"]
                    if is_today:
                        classes.append("today")
                    if has_jobs:
                        classes.append("has-jobs")

                    day_html = f'<div class="{" ".join(classes)}">{day_num}</div>'
                    calendar_days.append(day_html)
                else:
                    calendar_days.append('<div class="calendar-day"></div>')

        return "\n".join(calendar_days)

    async def interactive_session(self):
        """Run interactive prototyping session"""

        print("\n🎨 UI Rapid Prototyping Assistant")
        print("🚀 Powered by CreaTech - Creative Development Agent")
        print("=" * 60)

        while True:
            print("\n🎯 What would you like to do?")
            print("1. Analyze UI requirements")
            print("2. Generate UI concepts")
            print("3. Create prototype specification")
            print("4. Generate HTML prototype")
            print("5. Run complete prototyping workflow")
            print("6. View existing prototypes")
            print("7. Exit")

            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                description = input("Describe your UI requirements: ").strip()
                analysis = await self.analyze_ui_requirements(description)

                print("\n📊 Analysis Results:")
                print(f"   UI Challenges: {', '.join(analysis['ui_challenges'])}")
                print(f"   Workflow Complexity: {analysis['user_workflow_complexity']}")
                print(f"   Design Opportunities: {', '.join(analysis['design_opportunities'])}")

            elif choice == "2":
                description = input("Describe the UI you want to prototype: ").strip()
                analysis = await self.analyze_ui_requirements(description)
                concepts = await self.generate_ui_concepts(analysis)

                print("\n💡 Generated UI Concepts:")
                for i, concept in enumerate(concepts, 1):
                    print(f"   {i}. {concept['concept_name']}")
                    print(f"      Approach: {concept['design_approach']}")
                    print(f"      Complexity: {concept['prototype_complexity']}")
                    print(f"      Time: {concept['estimated_development_time']}")
                    print(f"      Confidence: {concept['confidence_score']:.1%}")

            elif choice == "3":
                description = input("Describe the UI for detailed specification: ").strip()
                analysis = await self.analyze_ui_requirements(description)
                concepts = await self.generate_ui_concepts(analysis, 1)

                if concepts:
                    specification = await self.create_prototype_specification(concepts[0], analysis)

                    print("\n📋 Prototype Specification Created:")
                    print(f"   Concept: {specification['concept_summary']['concept_name']}")
                    print(
                        f"   Technical Feasibility: {specification['confidence_assessment']['technical_feasibility']:.1%}"
                    )
                    print(f"   UX Quality: {specification['confidence_assessment']['user_experience_quality']:.1%}")
                    print(f"   Development Phases: {len(specification['implementation_plan']['development_phases'])}")

            elif choice == "4":
                print("⚠️  This requires a complete workflow analysis first.")
                print("Please use option 5 to run the complete workflow.")

            elif choice == "5":
                description = input("Describe the UI you want to prototype: ").strip()

                print("\n🚀 Running Complete Prototyping Workflow...")
                print("   Analyzing requirements...")
                analysis = await self.analyze_ui_requirements(description)

                print("   Generating UI concepts...")
                concepts = await self.generate_ui_concepts(analysis)

                if concepts:
                    print(f"   Creating specification for: {concepts[0]['concept_name']}")
                    specification = await self.create_prototype_specification(concepts[0], analysis)

                    print("   Generating HTML prototype...")
                    prototype_file = await self.generate_html_prototype(specification)

                    print("\n✅ Complete workflow finished!")
                    print(f"   Prototype saved: {prototype_file}")
                    print("   You can open this file in your browser to see the interactive prototype.")

            elif choice == "6":
                prototypes = list(self.workspace.glob("prototype-*.html"))
                if prototypes:
                    print("\n📁 Existing Prototypes:")
                    for prototype in prototypes:
                        print(f"   • {prototype.name}")
                else:
                    print("\n📁 No prototypes found. Generate one first!")

            elif choice == "7":
                print("\n👋 Thanks for using the UI Rapid Prototyping Assistant!")
                break
            else:
                print("Invalid choice. Please try again.")


# CLI interface
def main():
    """Main CLI interface for UI Rapid Prototyping Assistant"""
    parser = argparse.ArgumentParser(description="UI Rapid Prototyping Assistant - Powered by CreaTech")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--requirement", help="UI requirement to prototype")
    parser.add_argument("--workflow", action="store_true", help="Run complete prototyping workflow")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def run_cli():
        prototyper = UIRapidPrototyper()

        if args.interactive:
            await prototyper.interactive_session()
        elif args.requirement and args.workflow:
            print("🚀 Running Complete Prototyping Workflow...")
            print(f"   Requirement: {args.requirement}")

            analysis = await prototyper.analyze_ui_requirements(args.requirement)
            concepts = await prototyper.generate_ui_concepts(analysis)

            if concepts:
                specification = await prototyper.create_prototype_specification(concepts[0], analysis)
                prototype_file = await prototyper.generate_html_prototype(specification)

                print("\n✅ Workflow completed!")
                print(f"   Concept: {concepts[0]['concept_name']}")
                print(f"   Confidence: {concepts[0]['confidence_score']:.1%}")
                print(f"   Complexity: {concepts[0]['prototype_complexity']}")
                print(f"   Prototype: {prototype_file}")
        else:
            parser.print_help()

    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
