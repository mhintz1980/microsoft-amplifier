"""
Demo file for testing type error fixes
"""


class ContextCompactor:
    """Demo class for testing attribute access errors."""

    pass


async def test_function():
    """Test function with type errors."""
    # This will cause an attribute access error
    compactor = ContextCompactor()
    result = compactor.compress  # Missing 'compress' method  # type: ignore[attr-defined]

    # This will cause an await error
    awaitable_result = some_function()
    await awaitable_result  # 'object' is not awaitable

    # This will cause a None assignment error

    return result


def some_function():
    """Returns a non-awaitable object."""
    return "not awaitable"


# Test function that needs Optional fix
def get_name() -> str:  # Should be Optional[str]
    return None
