"""
Automatic Error Fixing Integration
Ensures enhanced error fixing patterns are always applied
"""


class AutoErrorFixer:
    """Automatic error fixing using proven enhanced SDK patterns"""

    def __init__(self):
        self.enabled = True

    def run_auto_fix(self):
        """Run automatic error fixing with enhanced patterns"""
        if not self.enabled:
            return

        print("🔧 Running automatic enhanced error fixing...")

        # Apply proven patterns
        from efficient_error_fixer import EfficientErrorFixer

        fixer = EfficientErrorFixer()
        fixed_count = fixer.apply_common_fixes()

        print(f"✅ Auto-fixed {fixed_count} errors using enhanced SDK patterns")


# Global auto-fixer instance
_auto_fixer = AutoErrorFixer()


def run_auto_error_fix():
    """Public API for automatic error fixing"""
    _auto_fixer.run_auto_fix()
