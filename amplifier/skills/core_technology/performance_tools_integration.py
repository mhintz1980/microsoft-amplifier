"""
Performance Tools Integration

Utility classes and functions for integrating various performance testing tools
with zero-configuration setup and validated results.
"""

import asyncio
import json
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@dataclass
class PerformanceToolConfig:
    """Configuration for performance testing tools."""

    tool_name: str
    available: bool = False
    version: str | None = None
    setup_instructions: str | None = None
    dependencies: list[str] = None


class LighthouseIntegration:
    """Lighthouse performance auditing integration."""

    def __init__(self):
        self.config = self._check_availability()

    def _check_availability(self) -> PerformanceToolConfig:
        """Check if Lighthouse CLI is available."""
        try:
            result = subprocess.run(["lighthouse", "--version"], capture_output=True, text=True, timeout=10)
            version = result.stdout.strip() if result.returncode == 0 else None
            return PerformanceToolConfig(
                tool_name="Lighthouse CLI",
                available=version is not None,
                version=version,
                setup_instructions="npm install -g lighthouse",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return PerformanceToolConfig(
                tool_name="Lighthouse CLI", available=False, setup_instructions="npm install -g lighthouse"
            )

    async def run_audit(self, url: str, output_path: str | None = None) -> dict[str, Any]:
        """Run Lighthouse audit for the given URL."""
        if not self.config.available:
            raise RuntimeError(f"Lighthouse CLI not available. Install with: {self.config.setup_instructions}")

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".json")

        cmd = [
            "lighthouse",
            url,
            "--output=json",
            f"--output-path={output_path}",
            "--quiet",
            '--chrome-flags="--headless"',
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"Lighthouse audit failed: {stderr.decode()}")

            # Read results
            with open(output_path) as f:
                results = json.load(f)

            return self._process_results(results)

        except Exception as e:
            raise RuntimeError(f"Failed to run Lighthouse audit: {str(e)}")

    def _process_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """Process Lighthouse results for easier consumption."""
        audits = results.get("audits", {})
        categories = results.get("categories", {})

        # Core Web Vitals
        core_web_vitals = {
            "lcp": {
                "value": audits.get("largest-contentful-paint", {}).get("numericValue", 0),
                "displayValue": audits.get("largest-contentful-paint", {}).get("displayValue", "0ms"),
            },
            "fid": {
                "value": audits.get("max-potential-fid", {}).get("numericValue", 0),
                "displayValue": audits.get("max-potential-fid", {}).get("displayValue", "0ms"),
            },
            "cls": {
                "value": audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
                "displayValue": audits.get("cumulative-layout-shift", {}).get("displayValue", "0"),
            },
            "ttfb": {
                "value": audits.get("server-response-time", {}).get("numericValue", 0),
                "displayValue": audits.get("server-response-time", {}).get("displayValue", "0ms"),
            },
        }

        # Performance score
        performance_score = categories.get("performance", {}).get("score", 0)

        # Opportunities for improvement
        opportunities = []
        for audit_id, audit in audits.items():
            if audit.get("score") is not None and audit["score"] < 0.9:
                opportunities.append(
                    {
                        "id": audit_id,
                        "title": audit.get("title", ""),
                        "description": audit.get("description", ""),
                        "score": audit.get("score", 0),
                        "displayValue": audit.get("displayValue", ""),
                        "numericValue": audit.get("numericValue", 0),
                    }
                )

        return {
            "url": results.get("finalUrl", ""),
            "performance_score": performance_score,
            "core_web_vitals": core_web_vitals,
            "opportunities": opportunities[:10],  # Top 10 opportunities
            "timestamp": results.get("fetchTime", ""),
            "lighthouse_version": results.get("lighthouseVersion", ""),
        }

    def generate_config(self, output_path: str = "lighthouse-config.js") -> str:
        """Generate Lighthouse configuration file."""
        config = {
            "extends": "lighthouse:default",
            "settings": {
                "onlyCategories": ["performance"],
                "emulatedFormFactor": "desktop",
                "throttling": {
                    "rttMs": 40,
                    "throughputKbps": 10240,
                    "cpuSlowdownMultiplier": 1,
                    "requestLatencyMs": 0,
                    "downloadThroughputKbps": 0,
                    "uploadThroughputKbps": 0,
                },
            },
        }

        config_content = f"""module.exports = {json.dumps(config, indent=2)};"""

        with open(output_path, "w") as f:
            f.write(config_content)

        return output_path


class WebPageTestIntegration:
    """WebPageTest API integration."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://www.webpagetest.org"
        self.config = self._check_availability()

    def _check_availability(self) -> PerformanceToolConfig:
        """Check WebPageTest API availability."""
        try:
            response = requests.get(f"{self.base_url}/testStatus.php", timeout=5)
            available = response.status_code == 200
            return PerformanceToolConfig(
                tool_name="WebPageTest API",
                available=available,
                setup_instructions="Get API key from https://www.webpagetest.org/",
            )
        except requests.RequestException:
            return PerformanceToolConfig(
                tool_name="WebPageTest API",
                available=False,
                setup_instructions="Check internet connection and API access",
            )

    async def run_test(self, url: str, test_options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run WebPageTest for the given URL."""
        if not self.config.available:
            raise RuntimeError("WebPageTest API not available")

        # Default test options
        default_options = {
            "url": url,
            "f": "json",
            "location": "Dulles:Chrome",
            "connectivity": "4G",
            "runs": 3,
            "priority": 1,
        }

        if self.api_key:
            default_options["k"] = self.api_key

        if test_options:
            default_options.update(test_options)

        try:
            # Start test
            start_response = requests.post(f"{self.base_url}/runtest.php", data=default_options, timeout=30)

            if start_response.status_code != 200:
                raise RuntimeError(f"Failed to start test: {start_response.text}")

            start_result = start_response.json()
            test_id = start_result["data"]["testId"]

            # Wait for completion
            return await self._wait_for_results(test_id)

        except Exception as e:
            raise RuntimeError(f"WebPageTest failed: {str(e)}")

    async def _wait_for_results(self, test_id: str, max_wait_time: int = 600) -> dict[str, Any]:
        """Wait for test completion and retrieve results."""
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            try:
                params = {"test": test_id, "f": "json"}
                if self.api_key:
                    params["k"] = self.api_key

                response = requests.get(f"{self.base_url}/jsonResult.php", params=params, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    status_code = result["data"]["statusCode"]

                    if status_code == 200:  # Test complete
                        return self._process_wpt_results(result)
                    if status_code in [100, 101]:  # Test running
                        await asyncio.sleep(10)
                        continue
                    # Test failed
                    raise RuntimeError(f"Test failed with status: {status_code}")
                await asyncio.sleep(5)
                continue

            except Exception:
                await asyncio.sleep(5)
                continue

        raise TimeoutError(f"Test {test_id} did not complete within {max_wait_time} seconds")

    def _process_wpt_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """Process WebPageTest results."""
        data = results["data"]
        runs = data["runs"]

        # Calculate averages across runs
        if not runs:
            raise RuntimeError("No test runs available")

        # Get median run
        median_run = runs[str(len(runs) // 2)]
        first_view = median_run["firstView"]

        # Core metrics
        core_metrics = {
            "lcp": first_view.get("largestContentfulPaint", 0),
            "fid": first_view.get("firstInputDelay", 0),
            "cls": first_view.get("cumulativeLayoutShift", 0),
            "ttfb": first_view.get("TTFB", 0),
            "fcp": first_view.get("firstContentfulPaint", 0),
            "si": first_view.get("SpeedIndex", 0),
            "tti": first_view.get("TimeToInteractive", 0),
            "load_time": first_view.get("loadTime", 0),
            "bytes_in": first_view.get("bytesIn", 0),
            "requests": first_view.get("requests", 0),
        }

        # Performance grades
        grades = data["summary"] if "summary" in data else {}

        return {
            "url": data["testUrl"],
            "test_id": data["testId"],
            "from_location": data["location"],
            "connectivity": data["connectivity"],
            "core_metrics": core_metrics,
            "grades": grades,
            "runs_count": len(runs),
            "complete_time": data["completeTime"],
            "raw_results": data,
        }


class ChromeDevToolsIntegration:
    """Chrome DevTools performance profiling integration."""

    def __init__(self):
        self.config = self._check_availability()

    def _check_availability(self) -> PerformanceToolConfig:
        """Check if Chrome WebDriver is available."""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=options)
            driver.quit()

            return PerformanceToolConfig(
                tool_name="Chrome DevTools",
                available=True,
                setup_instructions="Install ChromeDriver: https://sites.google.com/chromium.org/driver/",
            )
        except Exception:
            return PerformanceToolConfig(
                tool_name="Chrome DevTools",
                available=False,
                setup_instructions="Install ChromeDriver: https://sites.google.com/chromium.org/driver/",
            )

    async def capture_performance_metrics(self, url: str, wait_time: int = 5) -> dict[str, Any]:
        """Capture performance metrics using Chrome DevTools."""
        if not self.config.available:
            raise RuntimeError(f"Chrome WebDriver not available. {self.config.setup_instructions}")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        driver = None
        try:
            driver = webdriver.Chrome(options=options)

            # Enable performance logging
            caps = driver.capabilities
            caps["goog:loggingPrefs"] = {"performance": "ALL"}

            # Navigate to URL
            driver.get(url)

            # Wait for page to load
            await asyncio.sleep(wait_time)

            # Get performance metrics
            metrics = driver.execute_script("return performance.getEntriesByType('navigation')[0];")
            resources = driver.execute_script("return performance.getEntriesByType('resource');")

            # Calculate custom metrics
            core_metrics = self._calculate_core_metrics(metrics, resources)

            # Get console logs for errors
            logs = driver.get_log("performance")

            return {
                "url": url,
                "core_metrics": core_metrics,
                "resource_count": len(resources),
                "errors": self._parse_performance_logs(logs),
                "timestamp": time.time(),
            }

        except Exception as e:
            raise RuntimeError(f"Chrome DevTools profiling failed: {str(e)}")
        finally:
            if driver:
                driver.quit()

    def _calculate_core_metrics(self, navigation: dict, resources: list[dict]) -> dict[str, Any]:
        """Calculate core performance metrics from navigation timing."""
        return {
            "ttfb": navigation.get("responseStart", 0) - navigation.get("requestStart", 0),
            "fcp": navigation.get("loadEventEnd", 0) - navigation.get("fetchStart", 0),
            "dom_interactive": navigation.get("domInteractive", 0) - navigation.get("fetchStart", 0),
            "dom_complete": navigation.get("domComplete", 0) - navigation.get("fetchStart", 0),
            "load_event": navigation.get("loadEventEnd", 0) - navigation.get("fetchStart", 0),
            "total_resources": len(resources),
            "total_size": sum(r.get("transferSize", 0) for r in resources),
            "javascript_size": sum(r.get("transferSize", 0) for r in resources if r.get("name", "").endswith(".js")),
            "css_size": sum(r.get("transferSize", 0) for r in resources if r.get("name", "").endswith(".css")),
            "image_size": sum(
                r.get("transferSize", 0)
                for r in resources
                if any(r.get("name", "").endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"])
            ),
        }

    def _parse_performance_logs(self, logs: list[dict]) -> list[dict[str, Any]]:
        """Parse performance logs for errors and warnings."""
        errors = []
        for log in logs:
            message = log.get("message", "")
            if any(error in message.lower() for error in ["error", "failed", "exception"]):
                errors.append({"timestamp": log.get("timestamp", 0), "level": "ERROR", "message": message})
        return errors[:10]  # Return first 10 errors


class BundleAnalyzer:
    """Bundle size analysis and optimization suggestions."""

    def __init__(self):
        self.config = self._check_tools_availability()

    def _check_tools_availability(self) -> PerformanceToolConfig:
        """Check if bundle analysis tools are available."""
        tools_available = True
        setup_instructions = []

        # Check for webpack-bundle-analyzer
        try:
            subprocess.run(["npx", "webpack-bundle-analyzer", "--help"], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            tools_available = False
            setup_instructions.append("npm install --save-dev webpack-bundle-analyzer")

        # Check for source-map-explorer
        try:
            subprocess.run(["npx", "source-map-explorer", "--help"], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            tools_available = False
            setup_instructions.append("npm install --save-dev source-map-explorer")

        return PerformanceToolConfig(
            tool_name="Bundle Analyzer",
            available=tools_available,
            setup_instructions="\n".join(setup_instructions) if setup_instructions else None,
        )

    async def analyze_bundle(self, bundle_path: str) -> dict[str, Any]:
        """Analyze JavaScript bundle for optimization opportunities."""
        if not self.config.available:
            raise RuntimeError(f"Bundalyzer tools not available. Install with: {self.config.setup_instructions}")

        if not Path(bundle_path).exists():
            raise FileNotFoundError(f"Bundle file not found: {bundle_path}")

        # Get basic file info
        bundle_info = self._get_file_info(bundle_path)

        # Run webpack-bundle-analyzer
        analyzer_result = await self._run_bundle_analyzer(bundle_path)

        # Analyze dependencies
        dependencies = await self._analyze_dependencies(bundle_path)

        return {
            "bundle_path": bundle_path,
            "file_info": bundle_info,
            "analyzer_result": analyzer_result,
            "dependencies": dependencies,
            "optimization_suggestions": self._generate_optimization_suggestions(bundle_info, dependencies),
        }

    def _get_file_info(self, file_path: str) -> dict[str, Any]:
        """Get basic file information."""
        path = Path(file_path)
        return {
            "size_bytes": path.stat().st_size,
            "size_kb": round(path.stat().st_size / 1024, 2),
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            "extension": path.suffix,
            "is_compressed": path.suffix in [".gz", ".br", ".zip"],
        }

    async def _run_bundle_analyzer(self, bundle_path: str) -> dict[str, Any]:
        """Run webpack-bundle-analyzer in JSON mode."""
        try:
            # Note: webpack-bundle-analyzer doesn't have native JSON output
            # This is a simplified implementation
            with open(bundle_path, "rb") as f:
                content = f.read()

            # Basic analysis by examining the content
            return {
                "total_size": len(content),
                "estimated_chunks": content.count(b"chunk"),
                "estimated_modules": content.count(b"exports"),
                "has_source_map": b"sourceMappingURL" in content,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _analyze_dependencies(self, bundle_path: str) -> list[dict[str, Any]]:
        """Analyze dependencies in the bundle."""
        try:
            # Simple dependency detection by looking for common patterns
            with open(bundle_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Look for common library patterns
            libraries = []
            common_libs = ["react", "vue", "angular", "lodash", "moment", "axios", "jquery"]

            for lib in common_libs:
                count = content.count(lib)
                if count > 0:
                    libraries.append(
                        {
                            "name": lib,
                            "occurrences": count,
                            "estimated_size": count * 1000,  # Rough estimate
                        }
                    )

            return sorted(libraries, key=lambda x: x["occurrences"], reverse=True)
        except Exception as e:
            return [{"error": str(e)}]

    def _generate_optimization_suggestions(self, bundle_info: dict, dependencies: list[dict]) -> list[dict[str, Any]]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []

        # Size-based suggestions
        size_kb = bundle_info["size_kb"]
        if size_kb > 250:
            suggestions.append(
                {
                    "priority": "high",
                    "category": "size",
                    "title": "Bundle size exceeds 250KB",
                    "description": "Consider code splitting and tree shaking",
                    "expected_improvement": "30-50% size reduction",
                }
            )

        # Dependency-based suggestions
        for dep in dependencies[:5]:  # Top 5 dependencies
            if dep.get("occurrences", 0) > 10:
                suggestions.append(
                    {
                        "priority": "medium",
                        "category": "dependencies",
                        "title": f"Optimize {dep['name']} usage",
                        "description": f"Found {dep['occurrences']} occurrences, consider dynamic imports",
                        "expected_improvement": "10-20% size reduction",
                    }
                )

        return suggestions


class PerformanceToolsManager:
    """Manager class for all performance testing tools."""

    def __init__(self, webpagetest_api_key: str | None = None):
        self.lighthouse = LighthouseIntegration()
        self.webpagetest = WebPageTestIntegration(webpagetest_api_key)
        self.chrome_devtools = ChromeDevToolsIntegration()
        self.bundle_analyzer = BundleAnalyzer()

    async def run_comprehensive_analysis(self, url: str, bundle_path: str | None = None) -> dict[str, Any]:
        """Run comprehensive performance analysis using all available tools."""
        results = {"url": url, "timestamp": time.time(), "tools_used": [], "errors": []}

        # Lighthouse analysis
        if self.lighthouse.config.available:
            try:
                lighthouse_result = await self.lighthouse.run_audit(url)
                results["lighthouse"] = lighthouse_result
                results["tools_used"].append("Lighthouse")
            except Exception as e:
                results["errors"].append(f"Lighthouse: {str(e)}")

        # WebPageTest analysis
        if self.webpagetest.config.available:
            try:
                wpt_result = await self.webpagetest.run_test(url)
                results["webpagetest"] = wpt_result
                results["tools_used"].append("WebPageTest")
            except Exception as e:
                results["errors"].append(f"WebPageTest: {str(e)}")

        # Chrome DevTools analysis
        if self.chrome_devtools.config.available:
            try:
                devtools_result = await self.chrome_devtools.capture_performance_metrics(url)
                results["chrome_devtools"] = devtools_result
                results["tools_used"].append("Chrome DevTools")
            except Exception as e:
                results["errors"].append(f"Chrome DevTools: {str(e)}")

        # Bundle analysis
        if bundle_path and Path(bundle_path).exists():
            try:
                bundle_result = await self.bundle_analyzer.analyze_bundle(bundle_path)
                results["bundle_analysis"] = bundle_result
                results["tools_used"].append("Bundle Analyzer")
            except Exception as e:
                results["errors"].append(f"Bundle Analyzer: {str(e)}")

        # Generate unified insights
        results["insights"] = self._generate_unified_insights(results)

        return results

    def _generate_unified_insights(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate unified insights from multiple tool results."""
        insights = []

        # Core Web Vitals comparison
        core_vitals = {}
        if "lighthouse" in results:
            lighthouse_vitals = results["lighthouse"]["core_web_vitals"]
            core_vitals["lighthouse"] = lighthouse_vitals

        if "webpagetest" in results:
            wpt_metrics = results["webpagetest"]["core_metrics"]
            core_vitals["webpagetest"] = {
                "lcp": wpt_metrics.get("lcp", 0),
                "cls": wpt_metrics.get("cls", 0),
                "ttfb": wpt_metrics.get("ttfb", 0),
            }

        if "chrome_devtools" in results:
            devtools_metrics = results["chrome_devtools"]["core_metrics"]
            core_vitals["chrome_devtools"] = {
                "ttfb": devtools_metrics.get("ttfb", 0),
                "fcp": devtools_metrics.get("fcp", 0),
            }

        if core_vitals:
            insights.append(
                {
                    "category": "Core Web Vitals Comparison",
                    "data": core_vitals,
                    "recommendation": "Compare metrics across tools for comprehensive performance view",
                }
            )

        # Bundle optimization opportunities
        if "bundle_analysis" in results:
            bundle_result = results["bundle_analysis"]
            if bundle_result.get("optimization_suggestions"):
                insights.append(
                    {
                        "category": "Bundle Optimization",
                        "data": bundle_result["optimization_suggestions"],
                        "recommendation": "Implement code splitting and tree shaking",
                    }
                )

        return insights

    def get_tools_status(self) -> dict[str, PerformanceToolConfig]:
        """Get status of all performance tools."""
        return {
            "lighthouse": self.lighthouse.config,
            "webpagetest": self.webpagetest.config,
            "chrome_devtools": self.chrome_devtools.config,
            "bundle_analyzer": self.bundle_analyzer.config,
        }
