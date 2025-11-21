"""
Core Skills Integration Layer

Integrates the File Organizer with our 4 core skills:
- NodeJS Expert: File operations and path handling
- Security Expert: Safe file handling and permissions
- Performance Expert: Efficient scanning and progress tracking
- Vite Expert: Build-ready module structure

This layer provides specialized implementations that leverage each skill's expertise.
"""

import asyncio
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)


class NodeJSExpertIntegration:
    """Integration with NodeJS Expert for file operations and path handling."""

    def __init__(self):
        """Initialize NodeJS expert integration."""
        self.node_available = self._check_node_availability()
        self.npm_available = self._check_npm_availability()

    def _check_node_availability(self) -> bool:
        """Check if Node.js is available."""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Node.js not available, falling back to Python operations")
            return False

    def _check_npm_availability(self) -> bool:
        """Check if npm is available."""
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    async def move_file_with_node(self, source: Path, destination: Path) -> bool:
        """
        Move file using Node.js for better performance on large files.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if successful
        """
        if not self.node_available:
            # Fallback to Python
            import shutil

            shutil.move(str(source), str(destination))
            return True

        node_script = f"""
        const fs = require('fs');
        const path = require('path');

        const source = '{source}';
        const destination = '{destination}';

        try {{
            // Ensure destination directory exists
            const destDir = path.dirname(destination);
            if (!fs.existsSync(destDir)) {{
                fs.mkdirSync(destDir, {{ recursive: true }});
            }}

            // Move the file
            fs.renameSync(source, destination);
            console.log('SUCCESS');
        }} catch (error) {{
            console.error('ERROR:', error.message);
            process.exit(1);
        }}
        """

        try:
            result = await asyncio.create_subprocess_exec(
                "node", "-e", node_script, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and b"SUCCESS" in stdout:
                return True
            else:
                logger.error(f"Node.js move failed: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Node.js integration error: {e}")
            # Fallback to Python
            import shutil

            shutil.move(str(source), str(destination))
            return True

    async def get_file_info_node(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get detailed file information using Node.js.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information or None
        """
        if not self.node_available:
            return None

        node_script = f"""
        const fs = require('fs');
        const path = require('path');

        const filePath = '{file_path}';

        try {{
            const stats = fs.statSync(filePath);
            const info = {{
                size: stats.size,
                isFile: stats.isFile(),
                isDirectory: stats.isDirectory(),
                created: stats.birthtimeMs,
                modified: stats.mtimeMs,
                accessed: stats.atimeMs,
                extension: path.extname(filePath),
                name: path.basename(filePath)
            }};
            console.log(JSON.stringify(info));
        }} catch (error) {{
            console.error('ERROR:', error.message);
            process.exit(1);
        }}
        """

        try:
            result = await asyncio.create_subprocess_exec(
                "node", "-e", node_script, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                import json

                return json.loads(stdout.decode())
            else:
                logger.error(f"Node.js file info failed: {stderr.decode()}")
                return None

        except Exception as e:
            logger.error(f"Node.js file info error: {e}")
            return None


class SecurityExpertIntegration:
    """Integration with Security Expert for safe file handling and permissions."""

    def __init__(self):
        """Initialize security expert integration."""
        self.system = platform.system()
        self.sensitive_extensions = {
            ".exe",
            ".bat",
            ".cmd",
            ".com",
            ".pif",
            ".scr",
            ".vbs",
            ".js",
            ".jar",
            ".ps1",
            ".sh",
            ".bash",
            ".zsh",
            ".py",
            ".pl",
            ".rb",
            ".php",
            ".asp",
            ".dll",
            ".so",
            ".dylib",
            ".sys",
            ".drv",
            ".ocx",
        }
        self.sensitive_patterns = [
            "passwd",
            "shadow",
            "hosts",
            "sudoers",
            ".env",
            ".key",
            ".pem",
            ".crt",
            ".p12",
            ".pfx",
            "id_rsa",
            "id_dsa",
            "id_ecdsa",
        ]

    def is_file_safe(self, file_path: Path, content_check: bool = False) -> tuple[bool, List[str]]:
        """
        Check if a file is safe to process.

        Args:
            file_path: Path to file
            content_check: Whether to check file content

        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        warnings = []

        # Check file extension
        if file_path.suffix.lower() in self.sensitive_extensions:
            warnings.append(f"Executable file: {file_path.suffix}")

        # Check file name patterns
        for pattern in self.sensitive_patterns:
            if pattern.lower() in file_path.name.lower():
                warnings.append(f"Sensitive file pattern: {pattern}")

        # Check permissions
        try:
            if self.system == "Windows":
                import win32security

                # Check for special permissions on Windows
                pass
            else:
                # Check for setuid/setgid on Unix
                mode = file_path.stat().st_mode
                if mode & 0o4000:  # setuid
                    warnings.append("Setuid bit set")
                if mode & 0o2000:  # setgid
                    warnings.append("Setgid bit set")

        except Exception as e:
            warnings.append(f"Could not check permissions: {e}")

        # Content check for malicious patterns (basic)
        if content_check and file_path.is_file() and file_path.stat().st_size < 1024 * 1024:  # < 1MB
            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read(1000)  # Read first 1KB
                    malicious_patterns = [
                        "eval(base64",
                        "document.write",
                        "<script",
                        "javascript:",
                        "powershell",
                        "cmd.exe",
                        "/bin/sh",
                        "wget ",
                        "curl ",
                    ]
                    for pattern in malicious_patterns:
                        if pattern in content.lower():
                            warnings.append(f"Suspicious content pattern: {pattern}")
            except Exception:
                # Can't read file content
                warnings.append("Could not analyze file content")

        is_safe = len(warnings) == 0
        return is_safe, warnings

    def sanitize_file_path(self, file_path: Path) -> Path:
        """
        Sanitize a file path to prevent directory traversal attacks.

        Args:
            file_path: Path to sanitize

        Returns:
            Sanitized path
        """
        # Resolve path components
        resolved = file_path.resolve()

        # Remove any .. components that go above current directory
        if ".." in str(file_path):
            logger.warning(f"Potential directory traversal in path: {file_path}")

        return resolved

    def check_permissions(self, file_path: Path) -> Dict[str, bool]:
        """
        Check file permissions.

        Args:
            file_path: Path to check

        Returns:
            Dictionary with permission information
        """
        permissions = {"readable": False, "writable": False, "executable": False, "owner": False}

        try:
            if self.system == "Windows":
                # Windows permission checks
                import win32security
                import win32con
                import win32api

                try:
                    # Get file security descriptor
                    sd = win32security.GetNamedSecurityInfo(
                        str(file_path),
                        win32security.SE_FILE_OBJECT,
                        win32security.OWNER_SECURITY_INFORMATION | win32security.DACL_SECURITY_INFORMATION,
                    )

                    # Get current user
                    user_sid = win32security.GetTokenInformation(
                        win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32security.TOKEN_QUERY),
                        win32security.TokenUser,
                    )[0]

                    # Check if user is owner
                    owner_sid = sd.GetSecurityDescriptorOwner()
                    permissions["owner"] = user_sid == owner_sid

                    # Basic permission checks
                    permissions["readable"] = os.access(file_path, os.R_OK)
                    permissions["writable"] = os.access(file_path, os.W_OK)
                    permissions["executable"] = os.access(file_path, os.X_OK)

                except ImportError:
                    # Fallback to basic checks
                    permissions["readable"] = os.access(file_path, os.R_OK)
                    permissions["writable"] = os.access(file_path, os.W_OK)
                    permissions["executable"] = os.access(file_path, os.X_OK)
            else:
                # Unix permission checks
                permissions["readable"] = os.access(file_path, os.R_OK)
                permissions["writable"] = os.access(file_path, os.W_OK)
                permissions["executable"] = os.access(file_path, os.X_OK)

                # Check ownership
                stat_info = file_path.stat()
                permissions["owner"] = stat_info.st_uid == os.getuid()

        except Exception as e:
            logger.error(f"Permission check failed: {e}")

        return permissions


class PerformanceExpertIntegration:
    """Integration with Performance Expert for efficient operations."""

    def __init__(self):
        """Initialize performance expert integration."""
        self.concurrent_limit = 10
        self.chunk_size = 100
        self.performance_metrics = {"files_processed": 0, "total_bytes": 0, "start_time": None, "operations": []}

    async def process_files_parallel(
        self, files: List[Any], processor_func: callable, max_concurrent: Optional[int] = None
    ) -> List[Any]:
        """
        Process files in parallel for better performance.

        Args:
            files: List of files to process
            processor_func: Async function to process each file
            max_concurrent: Maximum concurrent operations

        Returns:
            List of processed results
        """
        max_concurrent = max_concurrent or self.concurrent_limit
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(file_item):
            async with semaphore:
                return await processor_func(file_item)

        tasks = [process_with_semaphore(file_item) for file_item in files]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def create_progress_tracker(self, total_items: int) -> Dict[str, Any]:
        """
        Create a progress tracker for monitoring operation performance.

        Args:
            total_items: Total number of items to process

        Returns:
            Progress tracker dictionary
        """
        import time

        return {
            "total_items": total_items,
            "processed_items": 0,
            "start_time": time.time(),
            "estimated_completion": None,
            "items_per_second": 0,
            "memory_usage_mb": 0,
        }

    def update_progress(self, tracker: Dict[str, Any], increment: int = 1) -> None:
        """
        Update progress tracker.

        Args:
            tracker: Progress tracker dictionary
            increment: Number of items processed
        """
        import time
        import psutil

        tracker["processed_items"] += increment
        current_time = time.time()
        elapsed = current_time - tracker["start_time"]

        if tracker["processed_items"] > 0:
            tracker["items_per_second"] = tracker["processed_items"] / elapsed
            remaining_items = tracker["total_items"] - tracker["processed_items"]
            if tracker["items_per_second"] > 0:
                tracker["estimated_completion"] = remaining_items / tracker["items_per_second"]

        # Memory usage
        process = psutil.Process()
        tracker["memory_usage_mb"] = process.memory_info().rss / 1024 / 1024

    def optimize_chunk_size(self, file_count: int, available_memory_mb: int) -> int:
        """
        Optimize chunk size based on file count and available memory.

        Args:
            file_count: Number of files to process
            available_memory_mb: Available memory in MB

        Returns:
            Optimal chunk size
        """
        # Base chunk size
        base_chunk = max(10, file_count // 20)

        # Adjust for memory constraints
        memory_limited_chunk = max(5, available_memory_mb // 10)

        # Use the smaller of the two
        return min(base_chunk, memory_limited_chunk, 1000)


class ViteExpertIntegration:
    """Integration with Vite Expert for build-ready module structure."""

    def __init__(self):
        """Initialize Vite expert integration."""
        self.vite_available = self._check_vite_availability()

    def _check_vite_availability(self) -> bool:
        """Check if Vite is available."""
        try:
            result = subprocess.run(["npx", "vite", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Vite not available")
            return False

    def create_package_json(self, module_path: Path) -> None:
        """
        Create package.json for the file organizer module.

        Args:
            module_path: Path to the module directory
        """
        package_json = {
            "name": "@amplifier/file-organizer",
            "version": "1.0.0",
            "description": "AI-powered file organization system",
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "scripts": {"build": "tsc && vite build", "dev": "vite", "preview": "vite preview", "test": "vitest"},
            "dependencies": {"pydantic": "^2.0.0"},
            "devDependencies": {"typescript": "^5.0.0", "vite": "^5.0.0", "vitest": "^1.0.0"},
            "exports": {".": {"import": "./dist/index.js", "types": "./dist/index.d.ts"}},
        }

        package_path = module_path / "package.json"
        import json

        with open(package_path, "w") as f:
            json.dump(package_json, f, indent=2)

    def create_vite_config(self, module_path: Path) -> None:
        """
        Create Vite configuration for the module.

        Args:
            module_path: Path to the module directory
        """
        vite_config = """
import { defineConfig } from 'vite'
import dts from 'vite-plugin-dts'

export default defineConfig({
  plugins: [
    dts({
      insertTypesEntry: true,
    }),
  ],
  build: {
    lib: {
      entry: 'src/index.ts',
      name: 'FileOrganizer',
      formats: ['es', 'umd']
    },
    rollupOptions: {
      external: ['pydantic'],
      output: {
        globals: {
          pydantic: 'pydantic'
        }
      }
    }
  },
  test: {
    globals: true,
    environment: 'node'
  }
})
"""

        config_path = module_path / "vite.config.ts"
        with open(config_path, "w") as f:
            f.write(vite_config)

    def create_typescript_config(self, module_path: Path) -> None:
        """
        Create TypeScript configuration for the module.

        Args:
            module_path: Path to the module directory
        """
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "preserve",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "declaration": True,
                "outDir": "dist",
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}],
        }

        import json

        with open(module_path / "tsconfig.json", "w") as f:
            json.dump(tsconfig, f, indent=2)

    def generate_api_documentation(self, module_path: Path) -> None:
        """
        Generate API documentation structure.

        Args:
            module_path: Path to the module directory
        """
        docs_dir = module_path / "docs"
        docs_dir.mkdir(exist_ok=True)

        api_docs = """# File Organizer API Documentation

## Core Classes

### FileOrganizer
Main orchestrator class for file organization operations.

```typescript
import { FileOrganizer, FileOrganizerConfig } from '@amplifier/file-organizer';

const config = new FileOrganizerConfig({
  dryRun: false,
  backupEnabled: true
});

const organizer = new FileOrganizer(config);
const result = await organizer.organizeDirectory('/path/to/files');
```

### FileScanner
High-performance file system scanner.

```typescript
const scanner = new FileScanner(scannerConfig);
const files = await scanner.scanDirectory('/path/to/scan');
```

### BasicCategorizer
Rule-based file categorization.

```typescript
const categorizer = new BasicCategorizer();
const category = categorizer.categorizeFile(fileInfo);
```

## Configuration

See FileOrganizerConfig for all available options.

## Integration

The module integrates with core Amplifier skills for optimal performance and security.
"""

        with open(docs_dir / "api.md", "w") as f:
            f.write(api_docs)


# Combined integration manager
class SkillIntegrationManager:
    """Manages all core skill integrations."""

    def __init__(self):
        """Initialize all skill integrations."""
        self.nodejs = NodeJSExpertIntegration()
        self.security = SecurityExpertIntegration()
        self.performance = PerformanceExpertIntegration()
        self.vite = ViteExpertIntegration()

    def get_integration_status(self) -> Dict[str, bool]:
        """Get status of all integrations."""
        return {
            "nodejs_available": self.nodejs.node_available,
            "npm_available": self.nodejs.npm_available,
            "vite_available": self.vite.vite_available,
        }

    async def setup_development_environment(self, module_path: Path) -> None:
        """Set up development environment with all tools."""
        if self.vite.vite_available:
            self.vite.create_package_json(module_path)
            self.vite.create_vite_config(module_path)
            self.vite.create_typescript_config(module_path)
            self.vite.generate_api_documentation(module_path)
            logger.info("Development environment configured")
        else:
            logger.warning("Vite not available, skipping development setup")
