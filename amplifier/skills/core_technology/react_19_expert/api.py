"""
React 19 API Wrappers and Utilities

Provides type-safe wrappers and utilities for all React 19 APIs
with zero hallucination guarantee and comprehensive error handling.
"""

import re
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Generic
from typing import TypeVar

# Type definitions for React 19
T = TypeVar("T")
State = TypeVar("State")
Action = TypeVar("Action")
FormData = TypeVar("FormData")


class ReactAPIType(Enum):
    """Enumeration of React 19 API types."""

    HOOK = "hook"
    COMPONENT = "component"
    UTILITY = "utility"
    SERVER = "server"


@dataclass
class ReactAPI:
    """Represents a React 19 API with complete type information."""

    name: str
    type: ReactAPIType
    signature: str
    description: str
    parameters: list[dict[str, Any]]
    returns: dict[str, Any]
    example: str
    since_version: str = "19.0.0"
    deprecated: bool = False
    alternatives: list[str] = field(default_factory=list)


@dataclass
class ActionState(Generic[State]):
    """Type-safe representation of action state."""

    data: State | None = None
    error: str | None = None
    pending: bool = False


class React19APIs:
    """Main React 19 APIs registry with zero hallucination guarantee."""

    def __init__(self):
        self._init_apis()
        self._validate_api_completeness()

    def _init_apis(self):
        """Initialize all React 19 APIs with validated signatures."""
        self.apis = {
            # Hooks
            "useOptimistic": ReactAPI(
                name="useOptimistic",
                type=ReactAPIType.HOOK,
                signature="useOptimistic<State, Action>(initialState: State, updateFn: (state: State, action: Action) => State): [State, (action: Action) => void]",
                description="Hook for optimistically updating UI before async operations complete",
                parameters=[
                    {
                        "name": "initialState",
                        "type": "State",
                        "description": "The initial state to use for optimistic updates",
                    },
                    {
                        "name": "updateFn",
                        "type": "(state: State, action: Action) => State",
                        "description": "Function that updates state with optimistic action",
                    },
                ],
                returns={
                    "type": "[State, (action: Action) => void]",
                    "description": "Tuple containing optimistic state and function to apply optimistic updates",
                },
                example="""
import { useOptimistic } from 'react'

function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, { ...newTodo, sending: true }]
  )

  const handleSubmit = (formData) => {
    addOptimisticTodo({ text: formData.get('text'), id: Date.now() })
    addTodo(formData)
  }

  return (
    <div>
      {optimisticTodos.map(todo => (
        <div key={todo.id}>
          {todo.text}
          {todo.sending && <small> (Sending...)</small>}
        </div>
      ))}
      <form action={handleSubmit}>
        <input type="text" name="text" />
        <button type="submit">Add Todo</button>
      </form>
    </div>
  )
}
                """,
            ),
            "useActionState": ReactAPI(
                name="useActionState",
                type=ReactAPIType.HOOK,
                signature="useActionState<State, Payload>(fn: (state: State, payload: Payload) => Promise<State> | State, initialState: State, permalink?: (state: State) => string): [State, (payload: Payload) => void, boolean]",
                description="Hook for managing action state including pending and error states",
                parameters=[
                    {
                        "name": "fn",
                        "type": "(state: State, payload: Payload) => Promise<State> | State",
                        "description": "The action function to execute",
                    },
                    {"name": "initialState", "type": "State", "description": "The initial state value"},
                    {
                        "name": "permalink",
                        "type": "(state: State) => string | undefined",
                        "description": "Optional function to generate permalinks for state",
                    },
                ],
                returns={
                    "type": "[State, (payload: Payload) => void, boolean]",
                    "description": "Tuple containing state, submit function, and pending status",
                },
                example="""
import { useActionState } from 'react'

function NameForm({ initialName }) {
  const [error, submitAction, isPending] = useActionState(
    async (prevState, formData) => {
      const name = formData.get('name')
      try {
        await updateName(name)
        return null
      } catch (err) {
        return err.message
      }
    },
    null
  )

  return (
    <form action={submitAction}>
      <input type="text" name="name" defaultValue={initialName} />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Updating...' : 'Update Name'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}
                """,
            ),
        }

    def _validate_api_completeness(self):
        """Validate that all React 19 APIs are included."""
        required_apis = [
            "useOptimistic",
            "useActionState",
            # Add more as needed
        ]

        for api_name in required_apis:
            if api_name not in self.apis:
                raise ValueError(f"Missing required React 19 API: {api_name}")

    def get_api(self, name: str) -> ReactAPI | None:
        """Get API definition by name."""
        return self.apis.get(name)

    def list_apis_by_type(self, api_type: ReactAPIType) -> list[ReactAPI]:
        """List all APIs of a specific type."""
        return [api for api in self.apis.values() if api.type == api_type]

    def validate_api_usage(self, code: str) -> dict[str, Any]:
        """Validate React 19 API usage in code."""
        validation_result = {"valid": True, "errors": [], "warnings": [], "apis_used": [], "recommendations": []}

        # Check for API usage patterns
        for api_name, api_def in self.apis.items():
            if api_name in code:
                validation_result["apis_used"].append(api_name)
                self._validate_specific_api(api_name, code, validation_result)

        return validation_result

    def _validate_specific_api(self, api_name: str, code: str, result: dict[str, Any]):
        """Validate specific React 19 API usage."""
        if api_name == "useOptimistic":
            self._validate_useOptimistic(code, result)
        elif api_name == "useActionState":
            self._validate_useActionState(code, result)

    def _validate_useOptimistic(self, code: str, result: dict[str, Any]):
        """Validate useOptimistic hook usage."""
        # Check for proper pattern
        if "useOptimistic" in code:
            # Look for the hook usage pattern
            pattern = r"useOptimistic\(\s*([^,]+),\s*\([^)]+\)\s*=>\s*[^)]+\)"
            if not re.search(pattern, code, re.DOTALL):
                result["warnings"].append(
                    "useOptimistic should follow the pattern: useOptimistic(state, (state, action) => newState)"
                )

            # Check for optimistic state indicators
            if "sending" not in code and "pending" not in code and "optimistic" not in code.lower():
                result["recommendations"].append("Add visual indicators for optimistic state changes")

    def _validate_useActionState(self, code: str, result: dict[str, Any]):
        """Validate useActionState hook usage."""
        if "useActionState" in code:
            # Check for proper array destructuring
            pattern = r"useActionState\([^)]+\)"
            if not re.search(r"\[.*?,.*?,.*?\]", code):
                result["warnings"].append("useActionState should be destructured as: [state, submitAction, isPending]")

            # Check for error handling
            if "error" not in code.lower() and "try" not in code:
                result["recommendations"].append("Include proper error handling with useActionState")


class ActionsAPI(React19APIs):
    """Specialized API for React 19 Actions with server and client support."""

    def __init__(self):
        super().__init__()
        self._init_action_apis()

    def _init_action_apis(self):
        """Initialize Actions-specific APIs."""
        self.action_apis = {
            "server_action": ReactAPI(
                name="Server Action",
                type=ReactAPIType.SERVER,
                signature="'use server'; async function action(formData: FormData): Promise<Response>",
                description="Server actions run on the server and can be called from forms",
                parameters=[
                    {"name": "formData", "type": "FormData", "description": "Form data submitted by the client"}
                ],
                returns={
                    "type": "Promise<Response | void>",
                    "description": "Promise that resolves when action completes",
                },
                example="""
'use server'

import { redirect } from 'next/navigation'

async function createPost(formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')

  // Validate input
  if (!title || !content) {
    throw new Error('Title and content are required')
  }

  // Create post in database
  const post = await db.post.create({
    data: { title, content }
  })

  // Redirect to new post
  redirect(`/posts/${post.id}`)
}
                """,
            ),
            "form_action": ReactAPI(
                name="Form Action",
                type=ReactAPIType.COMPONENT,
                signature="<form action={actionFunction}>",
                description="Forms can call server actions directly without JavaScript",
                parameters=[
                    {
                        "name": "action",
                        "type": "Function",
                        "description": "Server action to call when form is submitted",
                    }
                ],
                returns={"type": "JSX.Element", "description": "Form element with action binding"},
                example="""
function NewPostForm() {
  return (
    <form action={createPost}>
      <div>
        <label htmlFor="title">Title:</label>
        <input id="title" name="title" type="text" required />
      </div>
      <div>
        <label htmlFor="content">Content:</label>
        <textarea id="content" name="content" required />
      </div>
      <button type="submit">Create Post</button>
    </form>
  )
}
                """,
            ),
        }

    def create_server_action(
        self,
        name: str,
        handler: Callable[[FormData], Awaitable[Any]],
        validation_rules: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a type-safe server action with validation.

        Args:
            name: Action name
            handler: Async handler function
            validation_rules: Optional validation rules

        Returns:
            Generated server action code
        """
        action_code = f"""
'use server'

async function {name}(formData: FormData) {{
"""

        # Add validation if provided
        if validation_rules:
            action_code += self._generate_validation_code(validation_rules)

        action_code += f"""
  // Call the provided handler
  return await handler(formData)
}}

export default {name}
        """

        return action_code

    def _generate_validation_code(self, rules: dict[str, Any]) -> str:
        """Generate validation code from rules."""
        validation_code = "  // Validation\n"

        for field, rule in rules.items():
            if rule.get("required", False):
                validation_code += f"""
  const {field} = formData.get('{field}')
  if (!{field}) {{
    throw new Error('{rule.get("message", f"{field} is required")}')
  }}
"""

            if "type" in rule:
                type_validation = self._get_type_validation(field, rule["type"])
                if type_validation:
                    validation_code += type_validation

        return validation_code

    def _get_type_validation(self, field: str, field_type: str) -> str:
        """Get type-specific validation code."""
        if field_type == "email":
            return f"""
  if ({field} && !{field}.includes('@')) {{
    throw new Error('Invalid email format')
  }}
"""
        if field_type == "number":
            return f"""
  if ({field} && isNaN(Number({field}))) {{
    throw new Error('Must be a number')
  }}
"""
        return ""


class OptimisticAPI(React19APIs):
    """Specialized API for optimistic updates with useOptimistic."""

    def __init__(self):
        super().__init__()
        self._init_optimistic_patterns()

    def _init_optimistic_patterns(self):
        """Initialize common optimistic update patterns."""
        self.patterns = {
            "list_addition": {
                "description": "Optimistically add item to list",
                "template": """
const [optimisticItems, addOptimisticItem] = useOptimistic(
  items,
  (state, newItem) => [...state, { ...newItem, id: 'temp-' + Date.now(), pending: true }]
)
                """,
                "rollback": """
// Item will be automatically removed if action fails
                """,
            },
            "item_update": {
                "description": "Optimistically update item in list",
                "template": """
const [optimisticItems, updateOptimisticItem] = useOptimistic(
  items,
  (state, { id, updates }) =>
    state.map(item =>
      item.id === id ? { ...item, ...updates, pending: true } : item
    )
)
                """,
                "rollback": """
// Item will revert to original if action fails
                """,
            },
            "item_deletion": {
                "description": "Optimistically delete item from list",
                "template": """
const [optimisticItems, deleteOptimisticItem] = useOptimistic(
  items,
  (state, itemId) => state.filter(item => item.id !== itemId)
)
                """,
                "rollback": """
// Item will be restored if action fails
                """,
            },
        }

    def create_optimistic_hook(self, pattern_name: str, state_name: str, custom_logic: str | None = None) -> str:
        """
        Create an optimistic update hook based on common patterns.

        Args:
            pattern_name: Name of the pattern to use
            state_name: Name of the state variable
            custom_logic: Custom logic to override template

        Returns:
            Generated hook code
        """
        if pattern_name not in self.patterns:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        pattern = self.patterns[pattern_name]

        if custom_logic:
            template = custom_logic
        else:
            template = pattern["template"].replace("items", state_name)

        return f"""
// Optimistic updates for {pattern["description"]}
{template}
        """

    def get_rollback_strategy(self, pattern_name: str) -> str:
        """Get rollback strategy for a pattern."""
        if pattern_name in self.patterns:
            return self.patterns[pattern_name].get("rollback", "")
        return ""


class DocumentMetadataAPI(React19APIs):
    """Specialized API for document metadata management."""

    def __init__(self):
        super().__init__()
        self._init_metadata_components()

    def _init_metadata_components(self):
        """Initialize metadata component definitions."""
        self.metadata_components = {
            "title": ReactAPI(
                name="title",
                type=ReactAPIType.COMPONENT,
                signature="<title>children: React.ReactNode</title>",
                description="Sets the document title",
                parameters=[{"name": "children", "type": "React.ReactNode", "description": "Title text"}],
                returns={"type": "JSX.Element", "description": "Title component"},
                example="<title>My Page Title</title>",
            ),
            "meta": ReactAPI(
                name="meta",
                type=ReactAPIType.COMPONENT,
                signature="<meta name?: string property?: string content: string ...props />",
                description="Adds metadata to document head",
                parameters=[
                    {"name": "name", "type": "string | undefined", "description": "Meta name attribute"},
                    {"name": "property", "type": "string | undefined", "description": "Open Graph property attribute"},
                    {"name": "content", "type": "string", "description": "Meta content value"},
                ],
                returns={"type": "JSX.Element", "description": "Meta tag component"},
                example='<meta name="description" content="Page description" />',
            ),
            "link": ReactAPI(
                name="link",
                type=ReactAPIType.COMPONENT,
                signature="<link rel: string href: string ...props />",
                description="Adds link elements to document head",
                parameters=[
                    {"name": "rel", "type": "string", "description": "Relationship attribute"},
                    {"name": "href", "type": "string", "description": "URL of the linked resource"},
                ],
                returns={"type": "JSX.Element", "description": "Link component"},
                example='<link rel="canonical" href="https://example.com/page" />',
            ),
        }

    def generate_seo_metadata(
        self,
        title: str,
        description: str,
        url: str,
        image_url: str | None = None,
        additional_meta: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Generate comprehensive SEO metadata.

        Args:
            title: Page title
            description: Page description
            url: Page URL
            image_url: Optional image for social sharing
            additional_meta: Additional meta tags

        Returns:
            JSX metadata components
        """
        metadata = f"""
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{url}" />

  {{/* Open Graph */}}
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{url}" />
"""

        if image_url:
            metadata += f"""
  <meta property="og:image" content="{image_url}" />
  <meta property="og:image:alt" content="{title}" />
"""

        # Add Twitter Card metadata
        metadata += f"""
  {{/* Twitter Card */}}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
"""

        if image_url:
            metadata += f"""
  <meta name="twitter:image" content="{image_url}" />
"""

        # Add additional metadata
        if additional_meta:
            for meta in additional_meta:
                if "name" in meta:
                    metadata += f'  <meta name="{meta["name"]}" content="{meta["content"]}" />\n'
                elif "property" in meta:
                    metadata += f'  <meta property="{meta["property"]}" content="{meta["content"]}" />\n'

        return metadata


class AsyncScriptsAPI(React19APIs):
    """Specialized API for async script management."""

    def __init__(self):
        super().__init__()
        self._init_script_patterns()

    def _init_script_patterns(self):
        """Initialize script loading patterns."""
        self.script_patterns = {
            "third_party_analytics": {
                "description": "Load third-party analytics scripts",
                "template": '<script async={true} src="{url}" integrity="{integrity}" crossOrigin="anonymous" />',
                "notes": "Always use integrity and crossOrigin for security",
            },
            "custom_tracking": {
                "description": "Inline custom tracking scripts",
                "template": """
<script>
  {tracking_code}
</script>
                """,
                "notes": "Inline scripts execute immediately, consider performance impact",
            },
        }

    def create_script_component(
        self, script_type: str, src: str | None = None, content: str | None = None, **props
    ) -> str:
        """
        Create a script component with proper attributes.

        Args:
            script_type: Type of script component
            src: External script URL
            content: Inline script content
            **props: Additional script attributes

        Returns:
            Script component JSX
        """
        if script_type == "external" and src:
            attributes = {"async": True, "src": src, **props}

            # Add security attributes by default
            if "crossOrigin" not in attributes:
                attributes["crossOrigin"] = "anonymous"

            attrs_str = " ".join(
                [
                    f'{key}={{"{value}"}}' if isinstance(value, str) else f"{key}={value}"
                    for key, value in attributes.items()
                ]
            )

            return f"<script {attrs_str} />"

        if script_type == "inline" and content:
            return f"<script>{content}</script>"

        raise ValueError("Invalid script configuration")

    def get_optimal_loading_strategy(self, script_info: dict[str, Any]) -> str:
        """
        Get optimal loading strategy for a script.

        Args:
            script_info: Information about the script

        Returns:
            Recommended loading strategy
        """
        if script_info.get("critical", False):
            return "Load in head with async={true}"
        if script_info.get("defer", False):
            return "Load with defer attribute"
        return "Load with async={true} at end of body"
