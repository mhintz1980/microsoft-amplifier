#!/usr/bin/env python3
"""
Theme Factory Skill Test

Basic test to verify the Theme Factory integration works correctly.
Tests theme generation, CSS output, and HTML application.
"""

import asyncio
import tempfile
from pathlib import Path

from amplifier.skills.domain_expertise.theme_factory_skill import ThemeFactorySkill


async def test_theme_factory_basic():
    """Test basic ThemeFactorySkill functionality"""
    print("Testing Theme Factory Skill...")

    # Initialize the skill
    theme_skill = ThemeFactorySkill()
    print(f"✅ Skill initialized: {theme_skill.name}")

    # Test listing available themes
    print("\n1. Testing theme listing...")
    list_result = await theme_skill.execute({"action": "list_themes"})
    assert list_result.success, f"Failed to list themes: {list_result.error}"

    themes = list_result.data["available_themes"]
    print(f"✅ Found {len(themes)} themes:")
    for theme in themes[:3]:  # Show first 3
        print(f"   - {theme['name']}: {theme['description']}")

    # Test generating a specific theme
    print("\n2. Testing theme generation...")
    test_theme = "enterprise"
    generate_result = await theme_skill.execute({
        "action": "generate",
        "theme_name": test_theme
    })
    assert generate_result.success, f"Failed to generate theme: {generate_result.error}"

    html_content = generate_result.data["html_content"]
    css_content = generate_result.data["css_content"]
    print(f"✅ Generated {test_theme} theme:")
    print(f"   - HTML: {len(html_content)} characters")
    print(f"   - CSS: {len(css_content)} characters")
    print(f"   - Theme: {generate_result.data['theme_info']['name']}")

    # Test CSS-only generation
    print("\n3. Testing CSS-only generation...")
    css_result = await theme_skill.execute({
        "action": "generate_css",
        "theme_name": "creative"
    })
    assert css_result.success, f"Failed to generate CSS: {css_result.error}"

    css_only = css_result.data["css_content"]
    custom_props = css_result.data["custom_properties"]
    print(f"✅ Generated creative CSS:")
    print(f"   - CSS: {len(css_only)} characters")
    print(f"   - Custom properties: {len(custom_props)} variables")

    # Test custom theme generation
    print("\n4. Testing custom theme generation...")
    custom_result = await theme_skill.execute({
        "action": "custom_theme",
        "custom_theme": {
            "name": "test_custom",
            "description": "Test custom theme",
            "primary_color": "#ff6b6b",
            "secondary_color": "#4ecdc4",
            "background_color": "#ffffff"
        }
    })
    assert custom_result.success, f"Failed to generate custom theme: {custom_result.error}"

    custom_css = custom_result.data["css_content"]
    print(f"✅ Generated custom theme:")
    print(f"   - CSS: {len(custom_css)} characters")

    # Test content wrapping
    print("\n5. Testing content wrapping...")
    wrap_result = await theme_skill.execute({
        "action": "generate",
        "theme_name": "minimal",
        "target_content": "<h1>Test Content</h1><p>This is test content wrapped with theme.</p>"
    })
    assert wrap_result.success, f"Failed to wrap content: {wrap_result.error}"

    wrapped_html = wrap_result.data["html_content"]
    assert "Test Content" in wrapped_html, "Content not found in wrapped HTML"
    print(f"✅ Content wrapped successfully:")
    print(f"   - HTML: {len(wrapped_html)} characters")

    # Test skill capabilities
    print("\n6. Testing skill capabilities...")
    capabilities = theme_skill.get_capabilities()
    print(f"✅ Skill has {len(capabilities)} capabilities:")
    for cap in capabilities[:5]:  # Show first 5
        print(f"   - {cap}")

    # Test performance metrics
    print("\n7. Testing performance metrics...")
    metrics = theme_skill.performance_metrics
    print(f"✅ Performance metrics:")
    print(f"   - Themes generated: {metrics['themes_generated']}")
    print(f"   - CSS generated: {metrics['css_generated']}")
    print(f"   - Applications completed: {metrics['applications_completed']}")
    print(f"   - Average generation time: {metrics['average_generation_time']:.3f}s")

    print(f"\n🎉 All tests passed! Theme Factory skill is working correctly.")
    return True


async def test_theme_validation():
    """Test theme validation and error handling"""
    print("\nTesting Theme Factory validation...")

    theme_skill = ThemeFactorySkill()

    # Test invalid theme name
    print("1. Testing invalid theme name...")
    invalid_result = await theme_skill.execute({
        "action": "generate",
        "theme_name": "nonexistent_theme"
    })
    assert not invalid_result.success or "not found" in invalid_result.data.get("error", ""), "Should fail with invalid theme"
    print("✅ Invalid theme name properly handled")

    # Test invalid input
    print("2. Testing invalid input...")
    invalid_input_result = await theme_skill.execute(None)
    assert not invalid_input_result.success, "Should fail with None input"
    print("✅ Invalid input properly handled")

    # Test incomplete custom theme
    print("3. Testing incomplete custom theme...")
    incomplete_result = await theme_skill.execute({
        "action": "custom_theme",
        "custom_theme": {
            "name": "incomplete"
            # Missing required fields
        }
    })
    assert not incomplete_result.success or "Missing" in incomplete_result.data.get("error", ""), "Should fail with incomplete theme"
    print("✅ Incomplete custom theme properly handled")

    print("✅ All validation tests passed!")
    return True


async def test_theme_quality():
    """Test theme output quality and structure"""
    print("\nTesting theme output quality...")

    theme_skill = ThemeFactorySkill()

    # Test a few different themes
    test_themes = ["enterprise", "creative", "minimal", "midnight"]

    for theme_name in test_themes:
        print(f"1. Testing {theme_name} theme quality...")

        result = await theme_skill.execute({
            "action": "generate",
            "theme_name": theme_name
        })
        assert result.success, f"Failed to generate {theme_name} theme"

        html = result.data["html_content"]
        css = result.data["css_content"]

        # Validate HTML structure
        assert "<!DOCTYPE html>" in html, "HTML should have DOCTYPE"
        assert "<html" in html, "HTML should have html tag"
        assert "<head>" in html, "HTML should have head"
        assert "<body>" in html, "HTML should have body"
        assert "</html>" in html, "HTML should close properly"

        # Validate CSS content
        assert "--theme-primary:" in css, "CSS should have primary color variable"
        assert "--theme-background:" in css, "CSS should have background variable"
        assert "body {" in css, "CSS should have body styles"
        assert ".btn {" in css, "CSS should have button styles"

        # Check for accessibility features
        assert "focus" in css, "CSS should have focus styles"
        assert "@media" in css, "CSS should have responsive media queries"

        print(f"✅ {theme_name} theme quality validated")

    print("✅ All quality tests passed!")
    return True


def save_sample_output():
    """Save sample theme outputs for manual review"""
    print("\nSaving sample outputs...")

    async def _save_samples():
        theme_skill = ThemeFactorySkill()

        # Generate sample theme
        result = await theme_skill.execute({
            "action": "generate",
            "theme_name": "enterprise"
        })

        if result.success:
            # Save to temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(result.data["html_content"])
                html_file = f.name

            with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
                f.write(result.data["css_content"])
                css_file = f.name

            print(f"✅ Sample HTML saved to: {html_file}")
            print(f"✅ Sample CSS saved to: {css_file}")

            return html_file, css_file
        else:
            print("❌ Failed to generate sample")
            return None, None

    return asyncio.run(_save_samples())


async def main():
    """Run all tests"""
    print("🎨 Theme Factory Skill Test Suite")
    print("=" * 50)

    try:
        # Run core functionality tests
        await test_theme_factory_basic()

        # Run validation tests
        await test_theme_validation()

        # Run quality tests
        await test_theme_quality()

        # Save sample outputs
        save_sample_output()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("Theme Factory is ready for production use.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)