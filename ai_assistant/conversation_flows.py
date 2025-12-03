"""
Conversation Flow Management for Component Library Assistant

Intelligent conversation flows with state management, error handling,
and user experience optimization.
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid


class ConversationState(Enum):
    """States in conversation flow"""

    GREETING = "greeting"
    INTENT_UNDERSTANDING = "intent_understanding"
    INFORMATION_GATHERING = "information_gathering"
    ACTION_EXECUTION = "action_execution"
    CONFIRMATION = "confirmation"
    ERROR_RECOVERY = "error_recovery"
    CONVERSATION_END = "conversation_end"


class FlowTransition(Enum):
    """Types of flow transitions"""

    SUCCESS = "success"
    CLARIFICATION_NEEDED = "clarification_needed"
    ERROR_OCCURRED = "error_occurred"
    USER_INITIATED = "user_initiated"
    SYSTEM_INITIATED = "system_initiated"


@dataclass
class FlowNode:
    """Represents a node in conversation flow"""

    id: str
    state: ConversationState
    node_type: str  # 'response', 'question', 'action', 'validation'
    content: str
    next_nodes: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    fallback_node: Optional[str] = None
    validators: List[Callable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowContext:
    """Context for flow execution"""

    session_id: str
    user_id: str
    current_state: ConversationState
    previous_state: Optional[ConversationState] = None
    flow_data: Dict[str, Any] = field(default_factory=dict)
    user_inputs: List[Dict[str, Any]] = field(default_factory=list)
    system_outputs: List[Dict[str, Any]] = field(default_factory=list)
    error_count: int = 0
    success_count: int = 0
    conversation_start_time: datetime = field(default_factory=datetime.now)


class ConversationFlowEngine:
    """Manages conversation flows and state transitions"""

    def __init__(self, nlu_engine=None, response_generator=None):
        self.nlu_engine = nlu_engine
        self.response_generator = response_generator
        self.flows = self._load_conversation_flows()
        self.state_tracker = StateTracker()
        self.flow_history = []

    def _load_conversation_flows(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined conversation flows"""
        return {
            "save_component_flow": {
                "entry_points": ["save_component", "add_component"],
                "nodes": [
                    FlowNode(
                        id="validate_save_request",
                        state=ConversationState.INFORMATION_GATHERING,
                        node_type="validation",
                        content="validate_save_requirements",
                        next_nodes=["get_component_source"],
                        validators=[self._validate_save_requirements],
                    ),
                    FlowNode(
                        id="get_component_source",
                        state=ConversationState.INFORMATION_GATHERING,
                        node_type="question",
                        content="get_component_source",
                        next_nodes=["extract_component"],
                        fallback_node="manual_entry",
                        timeout=60,
                    ),
                    FlowNode(
                        id="extract_component",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="action",
                        content="extract_component_from_url",
                        next_nodes=["validate_extracted_data"],
                        fallback_node="save_with_manual_data",
                    ),
                    FlowNode(
                        id="validate_extracted_data",
                        state=ConversationState.VALIDATION,
                        node_type="validation",
                        content="validate_extracted_component",
                        next_nodes=["organize_component"],
                        validators=[self._validate_extracted_data],
                        fallback_node="save_with_issues",
                    ),
                    FlowNode(
                        id="organize_component",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="question",
                        content="suggest_component_organization",
                        next_nodes=["confirm_save"],
                        timeout=30,
                    ),
                    FlowNode(
                        id="confirm_save",
                        state=ConversationState.CONFIRMATION,
                        node_type="question",
                        content="confirm_component_save",
                        next_nodes=["execute_save"],
                        timeout=30,
                    ),
                    FlowNode(
                        id="execute_save",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="action",
                        content="execute_component_save",
                        next_nodes=["save_success"],
                        fallback_node="save_error",
                    ),
                ],
                "exit_points": ["save_success", "save_with_manual_data", "save_with_issues", "conversation_end"],
            },
            "search_components_flow": {
                "entry_points": ["search_components", "find_components"],
                "nodes": [
                    FlowNode(
                        id="understand_search_query",
                        state=ConversationState.INTENT_UNDERSTANDING,
                        node_type="validation",
                        content="analyze_search_intent",
                        next_nodes=["determine_search_strategy"],
                        validators=[self._validate_search_query],
                    ),
                    FlowNode(
                        id="determine_search_strategy",
                        state=ConversationState.INFORMATION_GATHERING,
                        node_type="decision",
                        content="choose_search_method",
                        next_nodes=["text_search", "category_search", "tag_search", "semantic_search"],
                        conditions={
                            "has_filters": "category_search",
                            "has_tags": "tag_search",
                            "semantic_needed": "semantic_search",
                            "simple_text": "text_search",
                        },
                    ),
                    FlowNode(
                        id="text_search",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="action",
                        content="execute_text_search",
                        next_nodes=["present_results"],
                        fallback_node="broaden_search",
                    ),
                    FlowNode(
                        id="present_results",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="response",
                        content="present_search_results",
                        next_nodes=["follow_up_actions"],
                        timeout=10,
                    ),
                    FlowNode(
                        id="follow_up_actions",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="question",
                        content="offer_follow_up_actions",
                        next_nodes=["conversation_end"],
                        timeout=30,
                    ),
                ],
                "exit_points": ["conversation_end", "broaden_search"],
            },
            "help_flow": {
                "entry_points": ["help", "tutorial", "getting_started"],
                "nodes": [
                    FlowNode(
                        id="assess_user_needs",
                        state=ConversationState.GREETING,
                        node_type="question",
                        content="assess_user_experience_level",
                        next_nodes=["provide_relevant_help"],
                        timeout=20,
                    ),
                    FlowNode(
                        id="provide_relevant_help",
                        state=ConversationState.INFORMATION_GATHERING,
                        node_type="response",
                        content="provide_comprehensive_help",
                        next_nodes=["offer_action_suggestions"],
                        timeout=15,
                    ),
                    FlowNode(
                        id="offer_action_suggestions",
                        state=ConversationState.ACTION_EXECUTION,
                        node_type="question",
                        content="suggest_next_actions",
                        next_nodes=["conversation_end"],
                        timeout=30,
                    ),
                ],
                "exit_points": ["conversation_end"],
            },
        }

    async def execute_flow(self, flow_id: str, context: FlowContext) -> Dict[str, Any]:
        """Execute a conversation flow"""
        if flow_id not in self.flows:
            return {"success": False, "error": f"Flow {flow_id} not found", "fallback_action": "provide_help"}

        flow = self.flows[flow_id]
        current_node = None
        flow_start_time = datetime.now()

        try:
            # Initialize flow
            if "entry_points" in flow:
                context.flow_data["entry_intent"] = flow["entry_points"][0]
                current_node = self._get_node(flow, flow["entry_points"][0])
            else:
                current_node = flow["nodes"][0]

            # Execute flow nodes
            while current_node:
                # Update context state
                context.previous_state = context.current_state
                context.current_state = current_node.state

                # Record flow transition
                self._record_flow_transition(flow_id, current_node.id, context)

                # Execute current node
                node_result = await self._execute_node(current_node, context)

                # Handle special actions
                if node_result.get("action") == "restart":
                    current_node = flow["nodes"][0] if flow["nodes"] else None
                    continue

                # Determine next node
                next_node_id = node_result.get(
                    "next_node", self._determine_next_node(current_node, node_result, context)
                )

                if next_node_id == "conversation_end":
                    break

                current_node = self._get_node(flow, next_node_id)

                # Check timeout
                if current_node and current_node.timeout:
                    if datetime.now() - flow_start_time > timedelta(seconds=current_node.timeout):
                        current_node = self._get_node(flow, current_node.fallback_node)
                        context.flow_data["timeout_occurred"] = True

            # Calculate flow metrics
            flow_duration = datetime.now() - flow_start_time
            context.flow_data["flow_id"] = flow_id
            context.flow_data["duration"] = flow_duration
            context.flow_data["nodes_executed"] = len(self.flow_history)

            return {
                "success": True,
                "flow_id": flow_id,
                "duration": flow_duration,
                "nodes_executed": len(self.flow_history),
                "flow_data": context.flow_data,
                "final_state": context.current_state,
            }

        except Exception as e:
            context.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "flow_id": flow_id,
                "error_count": context.error_count,
                "fallback_action": self._get_fallback_action(context),
            }

    async def _execute_node(self, node: FlowNode, context: FlowContext) -> Dict[str, Any]:
        """Execute a specific flow node"""
        node_result = {"node_id": node.id, "node_type": node.node_type, "success": True, "next_node": None, "data": {}}

        try:
            if node.node_type == "response":
                # Generate response using response generator
                response = await self.response_generator.generate_node_response(node.content, context)
                node_result["response"] = response
                context.system_outputs.append(
                    {"type": "response", "content": response, "timestamp": datetime.now(), "node_id": node.id}
                )

            elif node.node_type == "question":
                # Ask user for input
                question = await self._generate_question(node, context)
                node_result["question"] = question
                node_result["requires_input"] = True

            elif node.node_type == "action":
                # Execute specific action
                action_result = await self._execute_action(node.content, context)
                node_result.update(action_result)

            elif node.node_type == "validation":
                # Run validators
                validation_result = await self._run_validators(node.validators, context)
                node_result["validation"] = validation_result

                # If validation fails, determine next step
                if not validation_result.get("passed", True):
                    node_result["success"] = False
                    node_result["validation_errors"] = validation_result.get("errors", [])

            elif node.node_type == "decision":
                # Make decision based on conditions
                decision = await self._make_decision(node.conditions, context)
                node_result["decision"] = decision
                node_result["next_node"] = decision.get("next_node")

            # Run node-specific handlers
            if hasattr(self, f"_handle_{node.id}"):
                handler = getattr(self, f"_handle_{node.id}")
                handler_result = await handler(context, node_result)
                node_result.update(handler_result)

            return node_result

        except Exception as e:
            node_result["success"] = False
            node_result["error"] = str(e)
            return node_result

    def _get_node(self, flow: Dict[str, Any], node_id: str) -> Optional[FlowNode]:
        """Get a node from flow by ID"""
        for node in flow.get("nodes", []):
            if node.id == node_id:
                return node
        return None

    def _determine_next_node(self, current_node: FlowNode, node_result: Dict[str, Any], context: FlowContext) -> str:
        """Determine the next node based on current node and result"""
        if node_result.get("next_node"):
            return node_result["next_node"]

        if current_node.next_nodes:
            return current_node.next_nodes[0]  # Return first next_node

        return "conversation_end"

    def _record_flow_transition(self, flow_id: str, node_id: str, context: FlowContext):
        """Record flow transition for tracking"""
        self.flow_history.append(
            {
                "timestamp": datetime.now(),
                "flow_id": flow_id,
                "node_id": node_id,
                "state": context.current_state.value,
                "session_id": context.session_id,
                "user_id": context.user_id,
            }
        )

    def _get_fallback_action(self, context: FlowContext) -> str:
        """Get fallback action based on context"""
        if context.error_count > 2:
            return "escalate_to_human"
        return "provide_help"

    # Flow-specific handlers
    async def _handle_validate_save_requirements(
        self, context: FlowContext, node_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler for validating save requirements"""
        # This would integrate with the component library validation
        return {"passed": True, "missing_fields": [], "validation_errors": []}

    async def _handle_validate_extracted_data(
        self, context: FlowContext, node_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler for validating extracted component data"""
        # This would validate extracted component data
        return {"passed": True, "validation_errors": [], "warnings": []}

    async def _handle_save_with_manual_data(self, context: FlowContext, node_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for saving component with manual data entry"""
        return {"action": "manual_entry", "next_node": "manual_entry_form"}

    async def _handle_save_with_issues(self, context: FlowContext, node_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for saving component with issues"""
        return {"action": "resolve_issues", "next_node": "issue_resolution"}

    async def _generate_question(self, node: FlowNode, context: FlowContext) -> str:
        """Generate a question for the user"""
        if hasattr(self, f"_generate_question_{node.id}"):
            return await getattr(self, f"_generate_question_{node.id}")(context, node)

        # Default question generation
        return "I need some information to help you. Could you please provide details?"

    async def _generate_question_get_component_source(self, context: FlowContext, node: FlowNode) -> str:
        """Generate specific question for component source"""
        return """I can help you save components! Please choose one of these options:

**1️⃣ Extract from Website**
   - Provide a URL of the webpage
   - I'll automatically extract the component

**2️⃣ Manual Entry**
   - I can create a template
   - You'll provide the HTML, CSS, and JavaScript

**3️⃣ Upload Code**
   - Paste your component code directly
   - I'll organize it properly

Which option would you prefer?"""

    async def _generate_question_get_component_source_manual_entry(self, context: FlowContext, node: FlowNode) -> str:
        """Generate question for manual component entry"""
        return """Please provide the component code in the following format:

**HTML Code:**
```html
<!-- Your HTML code here -->
```

**CSS Code:**
```css
/* Your CSS styles here */
```

**JavaScript Code:**
```javascript
// Your JavaScript code here
```

**Component Details:**
- Name: What should I call this component?
- Description: Brief description of its purpose
- Tags: Keywords for finding it later

You can paste one section at a time, or provide everything at once."""

    async def _generate_question_organize_component(self, context: FlowContext, node: FlowNode) -> str:
        """Generate question for component organization"""
        return """I can help organize your component! Should I:

**1️⃣ Auto-Categorize**
   - Analyze the component code
   - Suggest appropriate category
   - Add relevant tags

**2️⃣ Manual Organization**
   - You choose the category
   - Specify tags manually
   - Organize by your preferences

**3️⃣ Keep as General**
   - Save to 'general' category
   - Add minimal tags

How would you like to organize this component?"""

    def _validate_save_requirements(self, context: FlowContext) -> Dict[str, Any]:
        """Validate requirements for saving a component"""
        # This would implement actual validation logic
        return {"passed": True, "missing_fields": [], "errors": []}

    def _validate_search_query(self, context: FlowContext) -> Dict[str, Any]:
        """Validate search query for completeness"""
        # This would implement actual validation logic
        return {"passed": True, "suggestions": []}

    def _validate_extracted_data(self, context: FlowContext) -> Dict[str, Any]:
        """Validate extracted component data"""
        # This would implement actual validation logic
        return {"passed": True, "warnings": [], "errors": []}


class StateTracker:
    """Tracks conversation state and history"""

    def __init__(self):
        self.state_history = []
        self.active_sessions = {}

    def track_state_transition(self, context: FlowContext, old_state: str, new_state: str):
        """Track state transitions"""
        transition = {
            "timestamp": datetime.now(),
            "session_id": context.session_id,
            "old_state": old_state,
            "new_state": new_state,
            "user_id": context.user_id,
        }

        self.state_history.append(transition)

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session states"""
        session_states = [transition for transition in self.state_history if transition["session_id"] == session_id]

        return {
            "session_id": session_id,
            "state_transitions": len(session_states),
            "most_common_state": self._get_most_common_state(session_states),
            "total_duration": self._calculate_session_duration(session_id),
            "success_rate": self._calculate_success_rate(session_id),
        }

    def _get_most_common_state(self, states: List[Dict[str, Any]]) -> str:
        """Find the most common state in the list"""
        state_counts = {}
        for transition in states:
            state = transition["new_state"]
            state_counts[state] = state_counts.get(state, 0) + 1

        return max(state_counts.items(), key=lambda x: x[1])[0] if state_counts else "unknown"

    def _calculate_session_duration(self, session_id: str) -> timedelta:
        """Calculate total session duration"""
        session_states = [transition for transition in self.state_history if transition["session_id"] == session_id]

        if len(session_states) < 2:
            return timedelta(0)

        start_time = session_states[0]["timestamp"]
        end_time = session_states[-1]["timestamp"]
        return end_time - start_time

    def _calculate_success_rate(self, session_id: str) -> float:
        """Calculate success rate for session"""
        session_states = [transition for transition in self.state_history if transition["session_id"] == session_id]

        if not session_states:
            return 0.0

        successful_states = sum(
            1 for state in session_states if state["new_state"] in ["action_execution", "conversation_end"]
        )

        return (successful_states / len(session_states)) * 100


# Usage example
if __name__ == "__main__":
    # This would be used for testing the conversation flow system
    async def test_conversation_flows():
        nlu_engine = None  # Would be initialized
        response_generator = None  # Would be initialized

        engine = ConversationFlowEngine(nlu_engine, response_generator)

        # Test context
        context = FlowContext(
            session_id=str(uuid.uuid4()),
            user_id="test_user",
            current_state=ConversationState.GREETING,
            conversation_start_time=datetime.now(),
        )

        # Test save component flow
        result = await engine.execute_flow("save_component_flow", context)
        print(f"Flow execution result: {result}")

    # Run test
    asyncio.run(test_conversation_flows())
