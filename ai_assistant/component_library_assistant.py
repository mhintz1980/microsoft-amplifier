"""
Component Library AI Assistant - Production-Ready Architecture

Advanced AI assistant for managing web component libraries with intelligent
conversation flow, context management, and LLM integration.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid


# Component Library Specific Types
@dataclass
class Component:
    """Represents a saved web component"""

    id: str
    name: str
    description: str
    html_code: str
    css_code: str
    js_code: str
    tags: List[str]
    category: str
    url_source: str
    date_saved: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "html_code": self.html_code,
            "css_code": self.css_code,
            "js_code": self.js_code,
            "tags": self.tags,
            "category": self.category,
            "url_source": self.url_source,
            "date_saved": self.date_saved.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class LibraryIndex:
    """Maintains searchable index of components"""

    components: List[Component] = field(default_factory=list)
    categories: Dict[str, List[str]] = field(default_factory=dict)
    tag_index: Dict[str, List[str]] = field(default_factory=dict)
    search_index: Dict[str, str] = field(default_factory=dict)  # keywords -> component_id
    last_updated: datetime = field(default_factory=datetime.now)


class IntentType(Enum):
    """Component library specific intents"""

    SAVE_COMPONENT = "save_component"
    SEARCH_COMPONENTS = "search_components"
    LIST_COMPONENTS = "list_components"
    GET_COMPONENT = "get_component"
    DELETE_COMPONENT = "delete_component"
    ORGANIZE_LIBRARY = "organize_library"
    UPDATE_INDEX = "update_index"
    HELP = "help"
    TECHNICAL_GUIDANCE = "technical_guidance"


@dataclass
class ConversationContext:
    """Maintains conversation state and context for component library"""

    session_id: str
    user_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    current_intent: Optional[IntentType] = None
    component_library: LibraryIndex = field(default_factory=LibraryIndex)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    working_component: Optional[Component] = None
    search_results: List[Component] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComponentLibraryAssistant:
    """Main AI assistant for component library management"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.nlu_engine = NLUEngine()
        self.dialog_manager = DialogManager()
        self.response_generator = ResponseGenerator()
        self.context_manager = ContextManager()
        self.component_store = ComponentStore()
        self.llm_client = LLMClient() if self.config.get("use_llm") else None

        # Component-specific handlers
        self.component_extractor = WebComponentExtractor()
        self.index_manager = IndexManager()

    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for component library assistant"""
        return {
            "max_context_messages": 20,
            "component_storage_path": "./component_library",
            "supported_formats": ["html", "react", "vue", "svelte", "angular"],
            "auto_categorization": True,
            "use_llm": True,
            "llm_model": "claude-3.5-sonnet",
            "similarity_threshold": 0.8,
            "max_search_results": 10,
        }

    async def process_message(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Process user message and generate intelligent response"""

        # Step 1: Update context with new message
        context = self.context_manager.update_context(message, context)

        # Step 2: Natural Language Understanding
        nlu_result = await self.nlu_engine.process_message(message, context)

        # Step 3: Dialog Management
        dialog_action = await self.dialog_manager.process_turn(context, nlu_result)

        # Step 4: Execute Action
        action_result = await self._execute_action(dialog_action, context)

        # Step 5: Generate Response
        response = await self.response_generator.generate_response(nlu_result["intent"], context, action_result)

        # Step 6: Update context with response
        context = self.context_manager.add_response(response, context)

        return {"response": response, "context": context, "action_result": action_result, "nlu_result": nlu_result}

    async def _execute_action(self, action: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
        """Execute the determined action"""
        action_type = action.get("type")

        handlers = {
            "save_component": self._handle_save_component,
            "search_components": self._handle_search_components,
            "list_components": self._handle_list_components,
            "get_component": self._handle_get_component,
            "organize_library": self._handle_organize_library,
            "update_index": self._handle_update_index,
            "extract_from_url": self._handle_extract_from_url,
            "generate_code": self._handle_generate_code,
        }

        handler = handlers.get(action_type, self._handle_unknown_action)
        return await handler(action, context)

    async def _handle_save_component(self, action: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
        """Handle saving a component to the library"""
        try:
            component_data = action.get("component_data", {})

            # Extract component if URL provided
            if "url" in component_data:
                extracted = await self.component_extractor.extract_from_url(
                    component_data["url"], component_data.get("selectors", {})
                )
                component_data.update(extracted)

            # Create component object
            component = Component(
                id=str(uuid.uuid4()),
                name=component_data.get("name", "Untitled Component"),
                description=component_data.get("description", ""),
                html_code=component_data.get("html_code", ""),
                css_code=component_data.get("css_code", ""),
                js_code=component_data.get("js_code", ""),
                tags=component_data.get("tags", []),
                category=component_data.get("category", "general"),
                url_source=component_data.get("url", "manual_entry"),
                date_saved=datetime.now(),
                metadata=component_data.get("metadata", {}),
            )

            # Auto-categorize if enabled
            if self.config["auto_categorization"] and not component.category:
                component.category = await self._auto_categorize_component(component)

            # Save to library
            await self.component_store.save_component(component)

            # Update index
            await self.index_manager.add_component(component, context.component_library)

            # Update context
            context.working_component = component

            return {
                "success": True,
                "component_id": component.id,
                "message": f"Component '{component.name}' saved successfully to {component.category} category",
                "component": component.to_dict(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save component. Please check the component data and try again.",
            }

    async def _handle_search_components(self, action: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
        """Handle component search request"""
        query = action.get("query", "")
        filters = action.get("filters", {})
        limit = min(action.get("limit", self.config["max_search_results"]), 50)

        # Search in library index
        search_results = await self.index_manager.search_components(
            query=query,
            category=filters.get("category"),
            tags=filters.get("tags", []),
            limit=limit,
            library=context.component_library,
        )

        # Update context with search results
        context.search_results = search_results

        return {
            "success": True,
            "results": [comp.to_dict() for comp in search_results],
            "query": query,
            "total_found": len(search_results),
        }

    async def _handle_extract_from_url(self, action: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
        """Handle component extraction from URL"""
        url = action.get("url")
        if not url:
            return {
                "success": False,
                "error": "URL required for extraction",
                "message": "Please provide a URL to extract components from.",
            }

        try:
            selectors = action.get("selectors", {})
            extracted = await self.component_extractor.extract_from_url(url, selectors)

            return {
                "success": True,
                "extracted_data": extracted,
                "url": url,
                "message": f"Successfully extracted components from {url}. You can now save them to your library.",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to extract components from {url}. Please check the URL and try again.",
            }

    async def _auto_categorize_component(self, component: Component) -> str:
        """Automatically categorize a component based on its content"""
        if not self.llm_client:
            return "general"

        # Use LLM to categorize
        prompt = f"""
Categorize this web component based on its code:

Component Name: {component.name}
Description: {component.description}
HTML Preview: {component.html_code[:200]}...
CSS Preview: {component.css_code[:200]}...

Available Categories:
- navigation (navbars, menus, breadcrumbs)
- forms (inputs, buttons, validation)
- layout (grids, containers, sections)
- ui-elements (cards, modals, tooltips)
- media (images, videos, carousels)
- data-display (tables, charts, lists)
- interactive (accordions, tabs, sliders)
- utility (helpers, utilities, mixins)

Category:"""

        try:
            response = await self.llm_client.generate(prompt, max_tokens=50, temperature=0.3)
            category = response.strip().lower()

            # Validate category
            valid_categories = [
                "navigation",
                "forms",
                "layout",
                "ui-elements",
                "media",
                "data-display",
                "interactive",
                "utility",
                "general",
            ]

            return category if category in valid_categories else "general"

        except Exception:
            return "general"


# Supporting Classes
class WebComponentExtractor:
    """Extracts web components from URLs"""

    async def extract_from_url(self, url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Extract component data from a URL"""
        import httpx
        from bs4 import BeautifulSoup

        selectors = selectors or {}

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract page title
            title = soup.find("title")
            page_title = title.get_text().strip() if title else url

            # Extract main content area
            content_selectors = selectors.get(
                "content", ["main", '[role="main"]', ".content", "#content", "article", ".component", ".widget"]
            )

            main_content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    break

            if not main_content:
                main_content = soup.find("body")

            # Extract HTML
            html_code = str(main_content)

            # Extract related CSS
            css_code = self._extract_css(soup, url)

            # Extract related JavaScript
            js_code = self._extract_js(soup, url)

            return {
                "name": page_title,
                "description": f"Component extracted from {url}",
                "html_code": html_code,
                "css_code": css_code,
                "js_code": js_code,
                "url_source": url,
                "metadata": {"extraction_date": datetime.now().isoformat(), "selectors_used": selectors},
            }

    def _extract_css(self, soup, base_url: str) -> str:
        """Extract relevant CSS from the page"""
        css_elements = soup.find_all(["style", "link"])
        css_code = []

        for element in css_elements:
            if element.name == "style":
                css_code.append(element.get_text())
            elif element.name == "link" and element.get("rel") == ["stylesheet"]:
                href = element.get("href")
                if href:
                    css_code.append(f"/* External CSS: {href} */")

        return "\n\n".join(css_code)

    def _extract_js(self, soup, base_url: str) -> str:
        """Extract relevant JavaScript from the page"""
        js_elements = soup.find_all(["script"])
        js_code = []

        for element in js_elements:
            if not element.get("src"):  # Inline scripts only
                js_code.append(element.get_text())

        return "\n\n".join(js_code)


# Add more supporting classes...
class NLUEngine:
    """Natural Language Understanding for component library"""

    async def process_message(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Process user message and extract intent and entities"""
        # Simplified implementation - in production, use actual NLU models
        message_lower = message.lower()

        # Intent detection
        intent = self._detect_intent(message_lower)

        # Entity extraction
        entities = self._extract_entities(message_lower, context)

        return {
            "intent": intent,
            "entities": entities,
            "confidence": 0.85,
            "requires_clarification": len(entities) == 0
            and intent in [IntentType.SAVE_COMPONENT, IntentType.SEARCH_COMPONENTS],
        }

    def _detect_intent(self, message: str) -> IntentType:
        """Detect user intent from message"""
        intent_keywords = {
            IntentType.SAVE_COMPONENT: ["save", "add", "store", "keep", "bookmark", "collect"],
            IntentType.SEARCH_COMPONENTS: ["search", "find", "look for", "get", "show me"],
            IntentType.LIST_COMPONENTS: ["list", "show all", "what components", "library"],
            IntentType.GET_COMPONENT: ["get component", "show component", "view component"],
            IntentType.DELETE_COMPONENT: ["delete", "remove", "delete component"],
            IntentType.ORGANIZE_LIBRARY: ["organize", "categorize", "sort", "clean up"],
            IntentType.HELP: ["help", "how to", "what can you do", "tutorial"],
            IntentType.TECHNICAL_GUIDANCE: ["how do i", "best practices", "implement"],
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in message for keyword in keywords):
                return intent

        return IntentType.HELP  # Default to help

    def _extract_entities(self, message: str, context: ConversationContext) -> List[Dict[str, Any]]:
        """Extract entities from message"""
        entities = []

        # Extract component names if they exist in library
        for component in context.component_library.components:
            if component.name.lower() in message:
                entities.append({"type": "component_name", "value": component.name, "component_id": component.id})

        # Extract categories
        categories = ["navigation", "forms", "layout", "ui-elements", "media", "data-display", "interactive"]
        for category in categories:
            if category in message:
                entities.append({"type": "category", "value": category})

        # Extract tags
        common_tags = ["responsive", "dark-mode", "mobile", "desktop", "bootstrap", "tailwind", "css3", "html5"]
        for tag in common_tags:
            if tag in message:
                entities.append({"type": "tag", "value": tag})

        return entities


class DialogManager:
    """Manages conversation flow and state"""

    async def process_turn(self, context: ConversationContext, nlu_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversation turn and determine next action"""
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]

        # Determine action based on intent
        if nlu_result.get("requires_clarification"):
            return {
                "type": "clarification_needed",
                "intent": intent,
                "clarification_questions": self._get_clarification_questions(intent, entities),
            }

        action_type = self._intent_to_action(intent)

        return {
            "type": action_type,
            "intent": intent,
            "entities": entities,
            "parameters": self._extract_parameters(intent, entities, context),
        }

    def _intent_to_action(self, intent: IntentType) -> str:
        """Map intent to action type"""
        action_mapping = {
            IntentType.SAVE_COMPONENT: "save_component",
            IntentType.SEARCH_COMPONENTS: "search_components",
            IntentType.LIST_COMPONENTS: "list_components",
            IntentType.GET_COMPONENT: "get_component",
            IntentType.DELETE_COMPONENT: "delete_component",
            IntentType.ORGANIZE_LIBRARY: "organize_library",
            IntentType.UPDATE_INDEX: "update_index",
            IntentType.HELP: "help",
            IntentType.TECHNICAL_GUIDANCE: "technical_guidance",
        }

        return action_mapping.get(intent, "help")

    def _get_clarification_questions(self, intent: IntentType, entities: List[Dict[str, Any]]) -> List[str]:
        """Generate clarification questions"""
        if intent == IntentType.SAVE_COMPONENT:
            if not any(e["type"] in ["component_name", "url"] for e in entities):
                return ["What component would you like to save?", "Do you have a URL I should extract from?"]
        elif intent == IntentType.SEARCH_COMPONENTS:
            if not any(e["type"] == "category" for e in entities):
                return [
                    "What type of components are you looking for?",
                    "Any specific tags or keywords I should search for?",
                ]

        return []

    def _extract_parameters(
        self, intent: IntentType, entities: List[Dict[str, Any]], context: ConversationContext
    ) -> Dict[str, Any]:
        """Extract parameters for action execution"""
        params = {}

        for entity in entities:
            if entity["type"] == "component_name":
                params["component_name"] = entity["value"]
                params["component_id"] = entity.get("component_id")
            elif entity["type"] == "category":
                params["category"] = entity["value"]
            elif entity["type"] == "tag":
                params.setdefault("tags", []).append(entity["value"])
            elif entity["type"] == "url":
                params["url"] = entity["value"]

        return params


class ResponseGenerator:
    """Generates contextual responses"""

    async def generate_response(
        self, intent: IntentType, context: ConversationContext, action_result: Dict[str, Any]
    ) -> str:
        """Generate response based on intent and action result"""
        response_templates = {
            IntentType.SAVE_COMPONENT: self._generate_save_response,
            IntentType.SEARCH_COMPONENTS: self._generate_search_response,
            IntentType.LIST_COMPONENTS: self._generate_list_response,
            IntentType.GET_COMPONENT: self._generate_get_response,
            IntentType.HELP: self._generate_help_response,
            IntentType.TECHNICAL_GUIDANCE: self._generate_guidance_response,
        }

        generator = response_templates.get(intent, self._generate_default_response)
        return await generator(action_result, context)

    async def _generate_save_response(self, action_result: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for component save action"""
        if action_result["success"]:
            component = action_result["component"]
            return f"""
✅ **Component Saved Successfully!**

**{component["name"]}** has been added to your component library.

📂 **Details:**
- **Category:** {component["category"]}
- **Tags:** {", ".join(component["tags"]) if component["tags"] else "None"}
- **ID:** {component["id"]}

You can now:
- Search for this component anytime
- Copy its code to other projects
- Find similar components by category or tags

What would you like to do next?
"""
        else:
            return f"""
❌ **Save Failed**

{action_result.get("message", "Unable to save the component.")}

Would you like me to help you fix the issue or try a different approach?
"""

    async def _generate_search_response(self, action_result: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for component search action"""
        if not action_result.get("results"):
            return f"""
🔍 **No Components Found**

I couldn't find any components matching your search for "{action_result.get("query", "")}".

Try:
- Searching with different keywords
- Browsing by category
- Checking your tags
"""

        components = action_result["results"]
        query = action_result["query"]
        total = action_result["total_found"]

        response = f"""
🔍 **Found {total} Components** for "{query}"

"""

        for i, component in enumerate(components[:5], 1):
            tags_text = ", ".join(component["tags"]) if component["tags"] else "No tags"
            response += f"""
**{i}. {component["name"]}**
   📁 Category: {component["category"]}
   🏷️  Tags: {tags_text}
   📅 ID: {component["id"]}
"""

        if total > 5:
            response += f"\n\n... and {total - 5} more components found. Showing top results."

        response += """

What would you like to do with these components?
- View details of a specific component
- Copy code from a component
- Search with different criteria
"""

        return response

    async def _generate_help_response(self, action_result: Dict[str, Any], context: ConversationContext) -> str:
        """Generate help response"""
        total_components = len(context.component_library.components)

        return f"""
🤖 **Component Library Assistant - Help**

I'm your AI assistant for managing web component libraries! Here's what I can help you with:

## 🛠️ **Core Features**
- **Save Components**: Extract and save components from any website
- **Search Library**: Find components by name, category, or tags
- **Get Components**: Retrieve specific components with full code
- **Organize Library**: Auto-categorize and tag components
- **Copy Code**: Generate paste-ready code for any project

## 📊 **Your Library Stats**
- **Total Components**: {total_components}
- **Categories**: {len(context.component_library.categories)}
- **Last Updated**: {context.component_library.last_updated.strftime("%Y-%m-%d %H:%M")}

## 💡 **Example Commands**
- "Save the navigation bar from example.com"
- "Search for form components"
- "Get the modal component with ID xyz123"
- "Organize my library by category"
- "Show me all responsive components"

## 🚀 **Getting Started**
1. **Extract**: Give me a URL to extract components from
2. **Search**: Ask me to find specific types of components
3. **Save**: I'll help you organize and save them
4. **Use**: Copy the code directly into your projects

What would you like to do first?
"""


class ContextManager:
    """Manages conversation context and state"""

    def update_context(self, message: str, context: ConversationContext) -> ConversationContext:
        """Update context with new message"""
        context.messages.append({"role": "user", "content": message, "timestamp": datetime.now()})

        # Maintain context size limit
        if len(context.messages) > 20:  # Keep last 20 messages
            context.messages = context.messages[-20:]

        return context

    def add_response(self, response: str, context: ConversationContext) -> ConversationContext:
        """Add AI response to context"""
        context.messages.append({"role": "assistant", "content": response, "timestamp": datetime.now()})

        return context


# Placeholder classes for full implementation
class ComponentStore:
    """Manages persistent storage of components"""

    async def save_component(self, component: Component):
        """Save component to storage"""
        # Implementation would save to file system or database
        pass


class IndexManager:
    """Manages searchable index of components"""

    async def search_components(
        self, query: str, category: str = None, tags: List[str] = None, limit: int = 10, library: LibraryIndex = None
    ) -> List[Component]:
        """Search components in the index"""
        # Implementation would perform semantic search
        return []


class LLMClient:
    """Client for LLM integration"""

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        # Implementation would integrate with Claude, GPT, etc.
        return "LLM response"
