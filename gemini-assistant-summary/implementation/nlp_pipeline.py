"""
Enhanced NLP Pipeline for Component Library Assistant

Advanced natural language processing with intent recognition,
entity extraction, and semantic understanding for component library requests.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import asyncio
from datetime import datetime
from dataclasses import dataclass


@dataclass
class NLUResult:
    """Natural Language Understanding result"""

    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    requires_clarification: bool
    semantic_understanding: Dict[str, Any]
    ambiguous_alternatives: List[str]


class EnhancedNLUEngine:
    """Advanced NLU engine with multiple recognition strategies"""

    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.semantic_analyzer = SemanticAnalyzer()

    async def process_message(self, message: str, context: Dict[str, Any]) -> NLUResult:
        """Process user message with comprehensive NLP analysis"""

        # Step 1: Preprocess message
        processed_message = self._preprocess_message(message)

        # Step 2: Parallel NLU tasks
        intent_task = self._detect_intent(processed_message, context)
        entity_task = self._extract_entities(processed_message, context)
        semantic_task = self._analyze_semantics(processed_message, context)

        # Execute tasks in parallel
        intent_result, entities_result, semantic_result = await asyncio.gather(intent_task, entity_task, semantic_task)

        # Step 3: Post-processing and validation
        final_intent = self._validate_intent(intent_result, processed_message)
        final_entities = self._resolve_entities(entities_result, context)
        requires_clarification = self._check_clarification_needed(final_intent, final_entities)

        return NLUResult(
            intent=final_intent,
            confidence=intent_result.get("confidence", 0.0),
            entities=final_entities,
            requires_clarification=requires_clarification,
            semantic_understanding=semantic_result,
            ambiguous_alternatives=intent_result.get("alternatives", []),
        )

    def _preprocess_message(self, message: str) -> str:
        """Preprocess user message for better NLU"""
        # Convert to lowercase
        message = message.lower()

        # Expand contractions
        contractions = {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "i'm": "i am",
            "it's": "it is",
            "that's": "that is",
            "we're": "we are",
            "they're": "they are",
            "you're": "you are",
            "i've": "i have",
            "we've": "we have",
            "you've": "you have",
        }

        for contraction, expansion in contractions.items():
            message = message.replace(contraction, expansion)

        # Remove extra whitespace
        message = re.sub(r"\s+", " ", message).strip()

        return message

    async def _detect_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect user intent with multiple strategies"""

        # Strategy 1: Pattern matching
        pattern_result = self._match_intent_patterns(message)

        # Strategy 2: Context-aware detection
        context_result = self._detect_context_intent(message, context)

        # Strategy 3: Semantic similarity (if LLM available)
        semantic_result = await self._detect_semantic_intent(message, context)

        # Combine results with confidence scoring
        combined_results = self._combine_intent_detections([pattern_result, context_result, semantic_result])

        return combined_results

    def _load_intent_patterns(self) -> Dict[str, Any]:
        """Load intent recognition patterns"""
        return {
            "save_component": {
                "keywords": [
                    "save",
                    "add",
                    "store",
                    "keep",
                    "bookmark",
                    "collect",
                    "grab",
                    "capture",
                    "extract",
                    "download",
                ],
                "patterns": [
                    r"(?:save|add|store|keep|bookmark)\s+(?:the\s+)?(?:component|element|widget)",
                    r"(?:extract|grab|capture|download)\s+(?:from\s+)?(?:the\s+)?(?:site|page|url)",
                    r"(?:i want to|i need to|help me)\s+(?:save|add|store)",
                    r"(?:can you|could you)\s+(?:save|add|store)\s+(?:this|it)",
                ],
                "confidence": 0.9,
            },
            "search_components": {
                "keywords": ["search", "find", "look for", "get", "show me", "list", "browse", "filter"],
                "patterns": [
                    r"(?:search|find|look for)\s+(?:for\s+)?(?:components?|elements?|widgets?)",
                    r"(?:show me|get|list)\s+(?:all\s+)?(?:my\s+)?(?:components?|library)",
                    r"(?:i have|do you have)\s+(?:a\s+)?(?:component|element)",
                    r"(?:find|search)\s+(?:by\s+)?(?:category|tag|name)",
                    r"(?:look for|find)\s+(?:something|anything)\s+(?:like|similar to)",
                ],
                "confidence": 0.85,
            },
            "get_component": {
                "keywords": ["get", "show", "view", "display", "open", "retrieve", "fetch"],
                "patterns": [
                    r"(?:get|show|view|display)\s+(?:the\s+)?(?:component|element)\s+(?:with|named)",
                    r"(?:open|retrieve|fetch)\s+(?:the\s+)?(?:component|element)",
                    r"(?:show me|let me see)\s+(?:the\s+)?(?:code for\s+)?(?:component|element)",
                    r"(?:i want to|i need)\s+(?:see|view|get)\s+(?:the\s+)?(?:component|element)",
                ],
                "confidence": 0.8,
            },
            "organize_library": {
                "keywords": ["organize", "categorize", "sort", "clean up", "manage", "structure", "arrange"],
                "patterns": [
                    r"(?:organize|categorize|sort)\s+(?:my\s+)?(?:library|components?)",
                    r"(?:clean up|manage)\s+(?:my\s+)?(?:component\s+)?(?:library|collection)",
                    r"(?:structure|arrange)\s+(?:the\s+)?(?:components?)\s+(?:by|with)",
                    r"(?:how should i|help me)\s+(?:organize|categorize)",
                ],
                "confidence": 0.75,
            },
            "delete_component": {
                "keywords": ["delete", "remove", "get rid of", "eliminate"],
                "patterns": [
                    r"(?:delete|remove|get rid of)\s+(?:the\s+)?(?:component|element)",
                    r"(?:i want to|i need to)\s+(?:delete|remove)\s+(?:this|the)",
                    r"(?:can you|could you)\s+(?:delete|remove)\s+(?:this|the)",
                ],
                "confidence": 0.9,
            },
            "help": {
                "keywords": ["help", "how to", "what can you do", "tutorial", "guide", "instructions"],
                "patterns": [
                    r"^\s*(?:help|how|what)\s*(?:can|do)\s*(?:you|i)",
                    r"(?:help me|tell me)\s+(?:how to|about)",
                    r"(?:what\s+can|do)\s+(?:you|i)\s+(?:do|help)",
                    r"(?:tutorial|guide|instructions)\s+(?:for|on)",
                    r"(?:getting started|beginner|new)",
                ],
                "confidence": 0.95,
            },
            "technical_guidance": {
                "keywords": ["how do i", "best practice", "implement", "integrate", "use"],
                "patterns": [
                    r"(?:how do i|how to)\s+(?:implement|integrate|use|work with)",
                    r"(?:best\s+practice|good\s+practice|proper\s+way)",
                    r"(?:what\s+is\s+the\s+best|how\s+should\s+i)",
                    r"(?:can\s+you\s+help\s+me\s+with|explain\s+how\s+to)",
                    r"(?:tell\s+me\s+about|explain\s+)",
                ],
                "confidence": 0.8,
            },
        }

    async def _extract_entities(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities with multiple extraction strategies"""
        entities = []

        # Strategy 1: Pattern-based extraction
        pattern_entities = self._extract_pattern_entities(message, context)
        entities.extend(pattern_entities)

        # Strategy 2: URL detection
        url_entities = self._extract_url_entities(message, context)
        entities.extend(url_entities)

        # Strategy 3: Component-specific entities
        component_entities = self._extract_component_entities(message, context)
        entities.extend(component_entities)

        # Strategy 4: Classification entities
        classification_entities = self._extract_classification_entities(message, context)
        entities.extend(classification_entities)

        # Strategy 5: Contextual entities (from library)
        contextual_entities = self._extract_contextual_entities(message, context)
        entities.extend(contextual_entities)

        return self._deduplicate_entities(entities)

    def _extract_url_entities(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract URLs from message"""
        url_pattern = r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?"
        urls = re.findall(url_pattern, message)

        entities = []
        for url in urls:
            if self._is_valid_url(url):
                entities.append(
                    {
                        "type": "url",
                        "value": url,
                        "start": message.find(url),
                        "end": message.find(url) + len(url),
                        "confidence": 0.95,
                    }
                )

        return entities

    def _extract_pattern_entities(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities using predefined patterns"""
        entities = []

        # Component name patterns
        component_patterns = [
            r'(?:"|`|\'|\')(?P<name>[^"`\'\s]+)(?:"|`|\'\')',
            r"(?:component|element)\s+(?:named|called)\s+(?P<name>\w+(?:\s+\w+)*)",
            r"(?:the\s+)?(?P<name>\w+(?:\s+\w+)*)\s+(?:component|element)",
        ]

        for pattern in component_patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                if "name" in match.groupdict():
                    entities.append(
                        {
                            "type": "component_name",
                            "value": match.group("name").strip(),
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.8,
                        }
                    )

        # Category patterns
        category_patterns = [
            r"(?:in\s+)?(?:the\s+)?(?P<category>navigation|forms|layout|ui-elements|media|data-display|interactive|utility)(?:\s+category)?",
            r"(?:category|type):\s*(?P<category>\w+)",
            r"(?:under|in)\s+(?P<category>\w+(?:\s+\w+)*)",
        ]

        for pattern in category_patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                if "category" in match.groupdict():
                    category = match.group("category")
                    if self._is_valid_category(category):
                        entities.append(
                            {
                                "type": "category",
                                "value": category,
                                "start": match.start(),
                                "end": match.end(),
                                "confidence": 0.85,
                            }
                        )

        # Tag patterns
        tag_patterns = [
            r"(?:tag[s]?\s*:?\s*|tags\s+(?:like|such as|including))\s*(?P<tags>[^.?!]+)",
            r"(?:with\s+)?(?P<tags>[\w-]+\s*(?:tags?|and)?)*)",
            r"(?:look\s+for|find)\s+(?P<tags>[\w-]+\s+(?:or|and)?)*)",
        ]

        for pattern in tag_patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                if "tags" in match.groupdict():
                    tags = re.split(r"[,;\s]+", match.group("tags"))
                    for tag in tags:
                        tag = tag.strip()
                        if tag and len(tag) > 1:
                            entities.append(
                                {
                                    "type": "tag",
                                    "value": tag,
                                    "start": match.start(),
                                    "end": match.end(),
                                    "confidence": 0.7,
                                }
                            )

        return entities

    def _extract_component_entities(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract component-specific entities"""
        entities = []

        # HTML element patterns
        html_patterns = [
            r"<(?P<tag>\w+)(?:\s+[^>]*)?>",
            r"(?:div|span|button|input|form|nav|header|footer|section|article)",
            r"(?:html|css|javascript|react|vue|angular|svelte)",
        ]

        for pattern in html_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                if "tag" in match.groupdict():
                    entities.append(
                        {
                            "type": "html_element",
                            "value": match.group("tag"),
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.75,
                        }
                    )

        # CSS property patterns
        css_patterns = [
            r"(?:css|style|design|theme)",
            r"(?:responsive|mobile|desktop|dark|light)\s*mode?",
            r"(?:flex|grid|layout|animation|transition)",
        ]

        for pattern in css_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                entities.append(
                    {
                        "type": "css_property",
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.7,
                    }
                )

        return entities

    def _extract_classification_entities(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract classification entities"""
        entities = []

        # Framework mentions
        frameworks = [
            "react",
            "vue",
            "angular",
            "svelte",
            "preact",
            "alpine",
            "stimulus",
            "htmx",
            "jquery",
            "bootstrap",
            "tailwind",
        ]
        for framework in frameworks:
            if framework.lower() in message:
                entities.append({"type": "framework", "value": framework, "confidence": 0.8})

        # Technology mentions
        technologies = [
            "javascript",
            "typescript",
            "html5",
            "css3",
            "nodejs",
            "python",
            "php",
            "ruby",
            "java",
            "c#",
            "go",
            "rust",
        ]
        for tech in technologies:
            if tech.lower() in message:
                entities.append({"type": "technology", "value": tech, "confidence": 0.75})

        return entities

    def _extract_contextual_entities(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from library context"""
        entities = []

        # This would integrate with the actual component library
        # For now, return empty list as placeholder

        return entities

    def _is_valid_url(self, url: str) -> bool:
        """Validate if string is a valid URL"""
        url_pattern = r"^(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$"
        return bool(re.match(url_pattern, url))

    def _is_valid_category(self, category: str) -> bool:
        """Validate if category is valid"""
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
        return category.lower() in valid_categories

    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities"""
        seen = set()
        deduplicated = []

        for entity in entities:
            entity_key = (entity["type"], entity["value"])
            if entity_key not in seen:
                seen.add(entity_key)
                deduplicated.append(entity)

        return deduplicated

    async def _analyze_semantics(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze semantic meaning of the message"""
        # This would implement more sophisticated semantic analysis
        # For now, return basic analysis

        return {
            "user_goal": self._infer_user_goal(message),
            "required_information": self._identify_missing_info(message, context),
            "conversation_phase": self._detect_conversation_phase(message, context),
            "urgency": self._assess_urgency(message),
            "complexity": self._assess_complexity(message),
        }

    def _infer_user_goal(self, message: str) -> str:
        """Infer the user's primary goal"""
        if any(word in message for word in ["save", "add", "store", "keep"]):
            return "save_component_to_library"
        elif any(word in message for word in ["find", "search", "look for", "get"]):
            return "retrieve_component_from_library"
        elif any(word in message for word in ["organize", "categorize", "sort", "manage"]):
            return "organize_component_library"
        elif any(word in message for word in ["delete", "remove", "get rid"]):
            return "remove_component_from_library"
        elif any(word in message for word in ["how", "help", "tutorial", "guide"]):
            return "learn_about_system"
        else:
            return "general_inquiry"

    def _identify_missing_info(self, message: str, context: Dict[str, Any]) -> List[str]:
        """Identify what information is missing"""
        missing = []

        # Check if component specification is clear
        if any(word in message for word in ["save", "add", "store"]):
            if not any(word in message for word in ["url", "website", "code", "html"]):
                missing.append("component_source")

        # Check if search criteria is specific
        if any(word in message for word in ["search", "find", "look for"]):
            if not any(word in message for word in ["category", "tag", "name"]):
                missing.append("search_criteria")

        return missing

    def _detect_conversation_phase(self, message: str, context: Dict[str, Any]) -> str:
        """Detect the current phase of conversation"""
        if not context.get("messages") or len(context["messages"]) < 3:
            return "initial_engagement"
        elif len(context["messages"]) < 10:
            return "information_gathering"
        else:
            return "task_execution"

    def _assess_urgency(self, message: str) -> str:
        """Assess the urgency of the request"""
        urgent_words = ["urgent", "emergency", "asap", "immediately", "quickly"]
        return "high" if any(word in message for word in urgent_words) else "normal"

    def _assess_complexity(self, message: str) -> str:
        """Assess the complexity of the request"""
        # Count technical terms
        technical_terms = ["component", "element", "html", "css", "javascript", "react", "vue", "angular", "api"]
        tech_count = sum(1 for word in message.split() if word.lower() in technical_terms)

        if tech_count >= 4:
            return "high"
        elif tech_count >= 2:
            return "medium"
        else:
            return "low"


class SemanticAnalyzer:
    """Advanced semantic analysis for better understanding"""

    def __init__(self):
        self.word_embeddings = {}  # Would load pre-trained embeddings
        self.semantic_patterns = self._load_semantic_patterns()

    def _load_semantic_patterns(self) -> Dict[str, Any]:
        """Load semantic analysis patterns"""
        return {
            "component_similarity": {
                "navigation": ["navbar", "menu", "header", "footer", "breadcrumb", "sidebar"],
                "forms": ["input", "button", "form", "field", "validation", "submission"],
                "layout": ["grid", "container", "section", "wrapper", "row", "column"],
                "ui_elements": ["card", "modal", "tooltip", "popover", "dropdown", "accordion"],
                "media": ["image", "video", "carousel", "gallery", "slider", "audio"],
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the NLP pipeline
    async def test_nlu_pipeline():
        engine = EnhancedNLUEngine()

        test_messages = [
            "Save the navigation bar from example.com",
            "Find me form components",
            "How do I organize my component library?",
            "Get the modal component with responsive design",
            "Help me extract a React component from this URL: https://example.com/components",
        ]

        for message in test_messages:
            result = await engine.process_message(message, {})
            print(f"Message: {message}")
            print(f"Intent: {result.intent} (confidence: {result.confidence})")
            print(f"Entities: {result.entities}")
            print(f"Requires clarification: {result.requires_clarification}")
            print("-" * 50)

    # Run test
    asyncio.run(test_nlu_pipeline())
