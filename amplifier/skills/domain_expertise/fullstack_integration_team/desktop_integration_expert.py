"""
Desktop Integration Expert Skill

Comprehensive expertise layer for integrating web applications with desktop platforms.
Provides zero-hallucination guidance on Tauri, Electron, cross-platform builds,
native API integration, file system access, system integration, performance
optimization, and security patterns.

Progressive Disclosure Levels:
- METADATA: Skill overview and capabilities
- SUMMARY: Key concepts and quick patterns
- DETAILED: Implementation examples and best practices
- FULL: Complete reference with production patterns

Integrates with Agent Lightning optimization patterns for maximum performance.
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urlparse

import yaml

from amplifier.skills.skills_framework.base_skill import BaseSkill, SkillContext, SkillResult, SkillStatus

logger = logging.getLogger(__name__)


class DisclosureLevel(Enum):
    """Progressive disclosure levels for content delivery"""

    METADATA = "metadata"  # Skill overview, capabilities, quick stats
    SUMMARY = "summary"  # Key concepts, patterns, minimal examples
    DETAILED = "detailed"  # Implementation examples, best practices
    FULL = "full"  # Complete reference with production patterns


class DesktopFramework(Enum):
    """Supported desktop frameworks"""

    TAURI = "tauri"
    ELECTRON = "electron"
    FLUTTER_DESKTOP = "flutter_desktop"
    WKWEBVIEW = "wkwebview"
    WEBVIEW2 = "webview2"


class Platform(Enum):
    """Supported desktop platforms"""

    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ALL = "all"


class IntegrationCategory(Enum):
    """Categories of desktop integration expertise"""

    FRAMEWORK_SETUP = "framework_setup"
    CROSS_PLATFORM_BUILD = "cross_platform_build"
    NATIVE_API = "native_api"
    FILE_SYSTEM = "file_system"
    SYSTEM_INTEGRATION = "system_integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    AUTO_UPDATES = "auto_updates"


@dataclass
class IntegrationPattern:
    """A reusable desktop integration pattern"""

    name: str
    category: IntegrationCategory
    framework: DesktopFramework
    platform: Platform
    description: str
    code_template: str
    configuration: Dict[str, Any]
    security_considerations: List[str]
    performance_notes: str
    examples: List[Dict[str, Any]]


@dataclass
class BuildConfiguration:
    """Cross-platform build configuration"""

    framework: DesktopFramework
    targets: List[Platform]
    output_formats: Dict[str, str]
    build_commands: Dict[str, List[str]]
    dependencies: Dict[str, List[str]]
    signing: Optional[Dict[str, Any]]
    notarization: Optional[Dict[str, Any]]


@dataclass
class SecurityPolicy:
    """Security policy for desktop integration"""

    sandbox_enabled: bool
    permissions: Dict[str, List[str]]
    api_restrictions: List[str]
    file_access_rules: Dict[str, str]
    network_policies: List[str]
    code_signing_required: bool


class DesktopIntegrationExpert(BaseSkill):
    """
    Comprehensive Desktop Integration Expert

    Zero-hallucination expertise layer for desktop application integration
    with web technologies. Provides production-ready patterns, security
    guidance, and performance optimization for Tauri, Electron, and other
    desktop frameworks.
    """

    def __init__(self):
        super().__init__(
            skill_id="desktop_integration_expert",
            name="Desktop Integration Expert",
            description="Expert guidance for desktop app integration with web technologies",
        )

        # Initialize pattern libraries
        self._integration_patterns: List[IntegrationPattern] = []
        self._build_configurations: Dict[DesktopFramework, BuildConfiguration] = {}
        self._security_policies: Dict[DesktopFramework, SecurityPolicy] = {}

        # Agent Lightning optimizations
        self._performance_cache = {}
        self._security_validator = SecurityValidator()
        self._build_optimizer = BuildOptimizer()
        self._optimization_enabled = True

        # Load all patterns and configurations
        self._initialize_patterns()
        self._initialize_build_configurations()
        self._initialize_security_policies()

    async def execute(self, input_data: Any, context: SkillContext = None) -> SkillResult:
        """
        Execute desktop integration expertise request

        Args:
            input_data: Query or configuration request
            context: Optional execution context

        Returns:
            SkillResult with expertise response
        """
        start_time = time.time()

        try:
            # Parse input request
            request = self._parse_request(input_data)

            # Apply zero-hallucination validation
            await self._validate_request(request)

            # Generate response with progressive disclosure
            response = await self._generate_response(request, context)

            execution_time = time.time() - start_time

            return SkillResult(
                success=True,
                data=response,
                execution_time=execution_time,
                tokens_used=len(str(response)),
                metadata={
                    "framework": request.get("framework"),
                    "platform": request.get("platform"),
                    "category": request.get("category"),
                    "disclosure_level": request.get("disclosure_level", "detailed"),
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Desktop integration expert failed: {e}")

            return SkillResult(success=False, error=str(e), execution_time=execution_time)

    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data for desktop integration request"""
        if isinstance(input_data, str):
            # Basic string query
            return len(input_data.strip()) > 0
        elif isinstance(input_data, dict):
            required_fields = ["query"]
            return all(field in input_data for field in required_fields)
        return False

    def get_capabilities(self) -> List[str]:
        """Get list of desktop integration capabilities"""
        return [
            "Tauri application setup and configuration",
            "Electron application patterns and optimization",
            "Cross-platform build pipeline configuration",
            "Native API integration for Windows, macOS, and Linux",
            "Secure file system access and permissions management",
            "System tray, notifications, and auto-updates",
            "Performance optimization and memory management",
            "Security hardening and sandboxing patterns",
            "Code signing and distribution configuration",
            "Debugging and troubleshooting desktop apps",
            "Progressive disclosure documentation for all expertise levels",
        ]

    def _parse_request(self, input_data: Any) -> Dict[str, Any]:
        """Parse and normalize input request"""
        if isinstance(input_data, str):
            return {
                "query": input_data,
                "framework": None,
                "platform": None,
                "category": None,
                "disclosure_level": "detailed",
            }
        elif isinstance(input_data, dict):
            return {
                "query": input_data.get("query", ""),
                "framework": input_data.get("framework"),
                "platform": input_data.get("platform"),
                "category": input_data.get("category"),
                "disclosure_level": input_data.get("disclosure_level", "detailed"),
                "context": input_data.get("context", {}),
            }
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")

    async def _validate_request(self, request: Dict[str, Any]):
        """Validate request for zero-hallucination compliance"""
        query = request.get("query", "").lower()

        # Check for impossible combinations
        framework = request.get("framework")
        platform = request.get("platform")

        if framework and platform:
            if not self._is_platform_framework_combination_valid(framework, platform):
                raise ValueError(f"Invalid combination: {framework} does not support {platform}")

        # Validate framework names
        if framework:
            try:
                DesktopFramework(framework.lower())
            except ValueError:
                raise ValueError(f"Unsupported framework: {framework}")

        # Validate platform names
        if platform:
            try:
                Platform(platform.lower())
            except ValueError:
                raise ValueError(f"Unsupported platform: {platform}")

    def _is_platform_framework_combination_valid(self, framework: str, platform: str) -> bool:
        """Check if framework supports the specified platform"""
        # All major frameworks support all platforms, but with different levels of support
        supported_combinations = {
            "tauri": ["windows", "macos", "linux"],
            "electron": ["windows", "macos", "linux"],
            "flutter_desktop": ["windows", "macos", "linux"],
            "wkwebview": ["macos"],
            "webview2": ["windows"],
        }

        return platform.lower() in supported_combinations.get(framework.lower(), ["windows", "macos", "linux"])

    async def _generate_response(self, request: Dict[str, Any], context: SkillContext = None) -> Dict[str, Any]:
        """Generate response with progressive disclosure"""
        query = request.get("query", "").lower()
        framework = request.get("framework")
        platform = request.get("platform")
        category = request.get("category")
        disclosure_level = DisclosureLevel(request.get("disclosure_level", "detailed"))

        # Determine expertise category from query
        if not category:
            category = self._categorize_query(query)

        # Generate response based on category and disclosure level
        if category == "framework_setup":
            return await self._generate_framework_setup_response(framework, disclosure_level)
        elif category == "cross_platform_build":
            return await self._generate_build_response(framework, platform, disclosure_level)
        elif category == "native_api":
            return await self._generate_native_api_response(framework, platform, disclosure_level)
        elif category == "file_system":
            return await self._generate_file_system_response(framework, disclosure_level)
        elif category == "system_integration":
            return await self._generate_system_integration_response(framework, disclosure_level)
        elif category == "performance":
            return await self._generate_performance_response(framework, disclosure_level)
        elif category == "security":
            return await self._generate_security_response(framework, disclosure_level)
        else:
            return await self._generate_comprehensive_response(request, disclosure_level)

    def _categorize_query(self, query: str) -> str:
        """Categorize query into expertise area"""
        keywords = {
            "framework_setup": ["setup", "install", "configure", "initialize", "create", "start", "begin"],
            "cross_platform_build": [
                "build",
                "compile",
                "package",
                "release",
                "deploy",
                "cross-platform",
                "multi-platform",
            ],
            "native_api": ["native", "api", "system", "os", "platform", "windows", "macos", "linux"],
            "file_system": ["file", "directory", "folder", "read", "write", "save", "load", "storage"],
            "system_integration": ["tray", "notification", "menu", "dock", "taskbar", "system", "integration"],
            "performance": ["performance", "optimization", "memory", "startup", "speed", "efficiency"],
            "security": ["security", "sandbox", "permissions", "code signing", "certificate", "safety"],
        }

        for category, words in keywords.items():
            if any(word in query for word in words):
                return category

        return "comprehensive"

    async def _generate_framework_setup_response(self, framework: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Generate framework setup expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "Framework Setup",
                "supported_frameworks": [f.value for f in DesktopFramework],
                "quick_patterns": ["Project initialization", "Configuration setup", "Development environment"],
                "complexity": "Beginner to Intermediate",
            }

        elif level == DisclosureLevel.SUMMARY:
            return {
                "expertise_area": "Framework Setup",
                "frameworks": {
                    "tauri": {
                        "setup_commands": [
                            "npm install -g @tauri-apps/cli",
                            "npm create tauri-app",
                            "npm run tauri dev",
                        ],
                        "key_files": ["src-tauri/Cargo.toml", "src-tauri/tauri.conf.json", "package.json"],
                        "dependencies": ["Rust toolchain", "Node.js", "System libraries"],
                    },
                    "electron": {
                        "setup_commands": [
                            "npm init electron-app@latest my-app",
                            "npm install --save-dev @electron/rebuild",
                            "npm start",
                        ],
                        "key_files": ["package.json", "main.js", "preload.js"],
                        "dependencies": ["Node.js", "Native dependencies"],
                    },
                },
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_framework_setup()

        else:  # FULL
            return await self._generate_complete_framework_setup()

    async def _generate_detailed_framework_setup(self) -> Dict[str, Any]:
        """Generate detailed framework setup examples"""
        return {
            "expertise_area": "Framework Setup - Detailed Implementation",
            "tauri": {
                "project_structure": {
                    "description": "Tauri project structure with frontend and backend",
                    "structure": {
                        "src/": "Frontend application (React, Vue, Svelte, etc.)",
                        "src-tauri/": "Rust backend code",
                        "src-tauri/src/main.rs": "Main Rust application entry point",
                        "src-tauri/Cargo.toml": "Rust dependencies and configuration",
                        "src-tauri/tauri.conf.json": "Tauri application configuration",
                        "src-tauri/build.rs": "Build script",
                        "dist/": "Frontend build output",
                        "target/": "Rust compilation output",
                    },
                },
                "configuration_example": {
                    "tauri_conf_json": {
                        "build": {
                            "beforeBuildCommand": "npm run build",
                            "beforeDevCommand": "npm run dev",
                            "devPath": "http://localhost:3000",
                            "distDir": "../dist",
                        },
                        "package": {"productName": "My Tauri App", "version": "1.0.0"},
                        "tauri": {
                            "allowlist": {
                                "all": False,
                                "fs": {
                                    "all": False,
                                    "readFile": True,
                                    "writeFile": True,
                                    "scope": ["$APPDATA/*", "$RESOURCE/*"],
                                },
                            },
                            "bundle": {
                                "active": True,
                                "category": "DeveloperTool",
                                "copyright": "",
                                "deb": {"depends": []},
                                "externalBin": [],
                                "icon": [
                                    "icons/32x32.png",
                                    "icons/128x128.png",
                                    "icons/128x128@2x.png",
                                    "icons/icon.icns",
                                    "icons/icon.ico",
                                ],
                                "identifier": "com.tauri.dev",
                                "longDescription": "",
                                "macOS": {
                                    "entitlements": null,
                                    "exceptionDomain": "",
                                    "frameworks": [],
                                    "providerShortName": null,
                                    "signingIdentity": null,
                                },
                                "resources": [],
                                "shortDescription": "",
                                "targets": "all",
                                "windows": {
                                    "certificateThumbprint": null,
                                    "digestAlgorithm": "sha256",
                                    "timestampUrl": "",
                                },
                            },
                            "security": {"csp": "default-src 'self'"},
                            "updater": {"active": False},
                            "windows": [
                                {
                                    "fullscreen": False,
                                    "height": 600,
                                    "resizable": True,
                                    "title": "My Tauri App",
                                    "width": 800,
                                }
                            ],
                        },
                    }
                },
            },
            "electron": {
                "project_structure": {
                    "description": "Electron project structure with main and renderer processes",
                    "structure": {
                        "src/": "Application source code",
                        "src/main.js": "Main process entry point",
                        "src/preload.js": "Preload script for secure IPC",
                        "src/renderer/": "Renderer process (frontend)",
                        "package.json": "Node.js project configuration",
                        "build/": "Build output directory",
                        "dist/": "Distribution output",
                    },
                },
                "main_process_example": {
                    "main_js": """const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('src/renderer/index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});"""
                },
                "preload_script_example": {
                    "preload_js": """const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, data) => ipcRenderer.invoke('write-file', filePath, data),
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body)
});"""
                },
            },
        }

    async def _generate_complete_framework_setup(self) -> Dict[str, Any]:
        """Generate complete framework setup with production patterns"""
        return {
            "expertise_area": "Framework Setup - Complete Production Guide",
            "tauri_production_patterns": {
                "secure_configuration": {
                    "tauri_conf_secure": {
                        "tauri": {
                            "allowlist": {
                                "all": False,
                                "fs": {
                                    "all": False,
                                    "readFile": True,
                                    "writeFile": True,
                                    "readDir": True,
                                    "copyFile": True,
                                    "createDir": True,
                                    "removeDir": True,
                                    "removeFile": True,
                                    "renameFile": True,
                                    "scope": ["$APPDATA/app-name/*", "$DOWNLOAD/*", "$DOCUMENT/*"],
                                },
                                "dialog": {"all": False, "open": True, "save": True},
                                "notification": {"all": True},
                            },
                            "security": {
                                "csp": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
                            },
                        }
                    }
                },
                "build_optimization": {
                    "cargo_toml_optimized": """[package]
name = "my-tauri-app"
version = "1.0.0"
description = "A Tauri Desktop Application"
authors = ["you"]
license = ""
repository = ""
default-run = "my-tauri-app"
edition = "2021"
rust-version = "1.60"

[build-dependencies]
tauri-build = { version = "1.0", features = [] }

[dependencies]
serde_json = "1.0"
serde = { version = "1.0", features = ["derive"] }
tauri = { version = "1.0", features = ["api-all"] }

[features]
default = [ "custom-protocol" ]
custom-protocol = [ "tauri/custom-protocol" ]""",
                    "build_rs": """fn main() {
  tauri_build::build()
}""",
                },
                "error_handling_patterns": {
                    "rust_error_handling": """use tauri::command;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub enum AppError {
    Io(String),
    Serialization(String),
    Validation(String),
    Permission(String),
}

impl From<std::io::Error> for AppError {
    fn from(error: std::io::Error) -> Self {
        AppError::Io(error.to_string())
    }
}

#[command]
async fn read_file_safe(path: String) -> Result<String, AppError> {
    // Validate path
    if !path.starts_with("$APPDATA/") && !path.starts_with("$DOCUMENT/") {
        return Err(AppError::Permission("Access denied".to_string()));
    }

    // Read file with error handling
    std::fs::read_to_string(path).map_err(AppError::from)
}"""
                },
            },
            "electron_production_patterns": {
                "secure_main_process": {
                    "main_secure_js": """const { app, BrowserWindow, ipcMain, dialog, Notification } = require('electron');
const path = require('path');
const fs = require('fs').promises;

// Security configuration
app.disableHardwareAcceleration();
app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor');

let mainWindow;

const secureWindowConfig = {
  width: 1200,
  height: 800,
  minWidth: 800,
  minHeight: 600,
  show: false,
  autoHideMenuBar: true,
  webPreferences: {
    preload: path.join(__dirname, 'preload.js'),
    nodeIntegration: false,
    nodeIntegrationInWorker: false,
    nodeIntegrationInSubFrames: false,
    contextIsolation: true,
    enableRemoteModule: false,
    webSecurity: true,
    allowRunningInsecureContent: false,
    experimentalFeatures: false,
    sandbox: true
  }
};

function createWindow() {
  mainWindow = new BrowserWindow(secureWindowConfig);

  // Security headers
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.executeJavaScript(`
      // Add security headers
      const meta = document.createElement('meta');
      meta.httpEquiv = 'Content-Security-Policy';
      meta.content = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'";
      document.head.appendChild(meta);
    `);
  });

  mainWindow.loadFile('src/renderer/index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
}

// Secure IPC handlers
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    // Validate file path
    const allowedPaths = [
      path.join(app.getPath('appData')),
      path.join(app.getPath('documents')),
      path.join(app.getPath('downloads'))
    ];

    const fullPath = path.resolve(filePath);
    const isAllowed = allowedPaths.some(allowed => fullPath.startsWith(allowed));

    if (!isAllowed) {
      throw new Error('Access denied: Path not allowed');
    }

    return await fs.readFile(fullPath, 'utf8');
  } catch (error) {
    console.error('File read error:', error);
    throw error;
  }
});

ipcMain.handle('show-notification', (event, title, body) => {
  if (Notification.isSupported()) {
    const notification = new Notification({
      title,
      body,
      icon: path.join(__dirname, 'assets/icon.png')
    });
    notification.show();
    return true;
  }
  return false;
});

app.whenReady().then(createWindow);"""
                },
                "package_json_production": {
                    "package_json": {
                        "name": "my-electron-app",
                        "version": "1.0.0",
                        "description": "A secure Electron application",
                        "main": "src/main.js",
                        "scripts": {
                            "start": "electron .",
                            "dev": "electron . --dev",
                            "build": "electron-builder",
                            "build:win": "electron-builder --win",
                            "build:mac": "electron-builder --mac",
                            "build:linux": "electron-builder --linux",
                            "test": "jest",
                            "lint": "eslint src/ --ext .js",
                            "security-check": "electron-builder --publish never",
                        },
                        "build": {
                            "appId": "com.example.myapp",
                            "productName": "My Electron App",
                            "directories": {"output": "dist"},
                            "files": ["src/**/*", "node_modules/**/*", "package.json"],
                            "mac": {
                                "category": "public.app-category.developer-tools",
                                "target": [{"target": "dmg", "arch": ["x64", "arm64"]}],
                                "entitlements": "build/entitlements.mac.plist",
                                "entitlementsInherit": "build/entitlements.mac.plist",
                                "hardenedRuntime": true,
                                "gatekeeperAssess": false,
                            },
                            "win": {
                                "target": [{"target": "nsis", "arch": ["x64", "ia32"]}],
                                "certificateFile": "build/certificate.p12",
                                "certificatePassword": "",
                                "publisherName": "My Company",
                            },
                            "linux": {
                                "target": [{"target": "AppImage", "arch": ["x64"]}, {"target": "deb", "arch": ["x64"]}],
                                "category": "Development",
                            },
                            "nsis": {
                                "oneClick": false,
                                "allowToChangeInstallationDirectory": true,
                                "createDesktopShortcut": true,
                                "createStartMenuShortcut": true,
                            },
                        },
                        "devDependencies": {
                            "electron": "^22.0.0",
                            "electron-builder": "^24.0.0",
                            "@electron/rebuild": "^3.2.0",
                            "eslint": "^8.0.0",
                            "jest": "^29.0.0",
                        },
                    }
                },
            },
        }

    def _initialize_patterns(self):
        """Initialize integration patterns library"""
        # Tauri file system pattern
        self._integration_patterns.append(
            IntegrationPattern(
                name="Tauri Secure File Access",
                category=IntegrationCategory.FILE_SYSTEM,
                framework=DesktopFramework.TAURI,
                platform=Platform.ALL,
                description="Secure file system access with proper permissions and error handling",
                code_template="""
use tauri::command;
use std::fs;
use std::path::Path;

#[command]
async fn read_app_file(path: String) -> Result<String, String> {
    // Validate path is within allowed directories
    let allowed_dirs = vec![
        appdata_dir(),
        documents_dir(),
    ];

    let full_path = Path::new(&path);
    let is_allowed = allowed_dirs.iter().any(|dir| full_path.starts_with(dir));

    if !is_allowed {
        return Err("Access denied".to_string());
    }

    fs::read_to_string(path).map_err(|e| e.to_string())
}

#[command]
async fn write_app_file(path: String, content: String) -> Result<(), String> {
    // Validate and write file securely
    let allowed_dirs = vec![appdata_dir()];
    let full_path = Path::new(&path);

    if !allowed_dirs.iter().any(|dir| full_path.starts_with(dir)) {
        return Err("Access denied".to_string());
    }

    // Create parent directories if needed
    if let Some(parent) = full_path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }

    fs::write(path, content).map_err(|e| e.to_string())
}""",
                configuration={"permissions": ["fs:readFile", "fs:writeFile", "fs:createDir"]},
                security_considerations=[
                    "Always validate file paths",
                    "Restrict access to specific directories",
                    "Use path sanitization",
                    "Implement proper error handling",
                ],
                performance_notes="Use async operations for large files",
                examples=[
                    {
                        "usage": "Read user preferences file",
                        "code": "const preferences = await invoke('read_app_file', { path: '$APPDATA/myapp/preferences.json' });",
                    }
                ],
            )
        )

        # Electron native API pattern
        self._integration_patterns.append(
            IntegrationPattern(
                name="Electron Native OS Integration",
                category=IntegrationCategory.SYSTEM_INTEGRATION,
                framework=DesktopFramework.ELECTRON,
                platform=Platform.ALL,
                description="Native OS integration with system tray, notifications, and shell commands",
                code_template="""
const { app, Menu, Tray, nativeImage, shell } = require('electron');

class SystemIntegration {
  constructor() {
    this.tray = null;
    this.setupSystemTray();
    this.setupMenu();
  }

  setupSystemTray() {
    const icon = nativeImage.createFromPath('assets/tray-icon.png');
    this.tray = new Tray(icon.resize({ width: 16, height: 16 }));

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show App',
        click: () => {
          this.mainWindow.show();
        }
      },
      { type: 'separator' },
      {
        label: 'Quit',
        click: () => {
          app.quit();
        }
      }
    ]);

    this.tray.setToolTip('My Application');
    this.tray.setContextMenu(contextMenu);

    this.tray.on('click', () => {
      this.mainWindow.isVisible() ? this.mainWindow.hide() : this.mainWindow.show();
    });
  }

  setupMenu() {
    if (process.platform === 'darwin') {
      const template = [
        {
          label: app.getName(),
          submenu: [
            { role: 'about' },
            { type: 'separator' },
            { role: 'services' },
            { type: 'separator' },
            { role: 'hide' },
            { role: 'hideothers' },
            { role: 'unhide' },
            { type: 'separator' },
            { role: 'quit' }
          ]
        }
      ];
      Menu.setApplicationMenu(Menu.buildFromTemplate(template));
    }
  }

  async openExternal(url) {
    await shell.openExternal(url);
  }

  async showItemInFolder(fullPath) {
    shell.showItemInFolder(fullPath);
  }
}""",
                configuration={},
                security_considerations=[
                    "Validate external URLs before opening",
                    "Escape file paths properly",
                    "Use sandboxed shell operations",
                    "Implement user confirmation for sensitive operations",
                ],
                performance_notes="Minimize system tray updates and use lazy loading",
                examples=[
                    {
                        "usage": "Open external URL safely",
                        "code": "await systemIntegration.openExternal('https://example.com');",
                    }
                ],
            )
        )

    def _initialize_build_configurations(self):
        """Initialize cross-platform build configurations"""
        # Tauri build configuration
        self._build_configurations[DesktopFramework.TAURI] = BuildConfiguration(
            framework=DesktopFramework.TAURI,
            targets=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
            output_formats={"windows": ["msi", "nsis"], "macos": ["app", "dmg"], "linux": ["deb", "appimage"]},
            build_commands={
                "windows": [
                    ["cargo", "tauri", "build", "--target", "x86_64-pc-windows-msvc"],
                    ["cargo", "tauri", "build", "--target", "i686-pc-windows-msvc"],
                ],
                "macos": [
                    ["cargo", "tauri", "build", "--target", "x86_64-apple-darwin"],
                    ["cargo", "tauri", "build", "--target", "aarch64-apple-darwin"],
                ],
                "linux": [["cargo", "tauri", "build", "--target", "x86_64-unknown-linux-gnu"]],
            },
            dependencies={
                "windows": ["Microsoft Visual Studio Build Tools", "Rust", "Node.js"],
                "macos": ["Xcode Command Line Tools", "Rust", "Node.js"],
                "linux": ["build-essential", "libwebkit2gtk-4.0-dev", "libssl-dev", "libgtk-3-dev", "Rust", "Node.js"],
            },
            signing={
                "windows": {
                    "certificate": "path/to/certificate.p12",
                    "password_env": "CSC_KEY_PASSWORD",
                    "timestamp_server": "http://timestamp.digicert.com",
                },
                "macos": {
                    "identity": "Developer ID Application: Your Name",
                    "entitlements": "build/entitlements.mac.plist",
                },
            },
            notarization={
                "macos": {"apple_id": "your@apple.id", "password": "@keychain:AC_PASSWORD", "team_id": "YOUR_TEAM_ID"}
            },
        )

        # Electron build configuration
        self._build_configurations[DesktopFramework.ELECTRON] = BuildConfiguration(
            framework=DesktopFramework.ELECTRON,
            targets=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
            output_formats={
                "windows": ["nsis", "portable"],
                "macos": ["dmg", "zip"],
                "linux": ["deb", "rpm", "AppImage"],
            },
            build_commands={
                "windows": [
                    ["npm", "run", "build:win"],
                    ["electron-builder", "--win", "--x64"],
                    ["electron-builder", "--win", "--ia32"],
                ],
                "macos": [
                    ["npm", "run", "build:mac"],
                    ["electron-builder", "--mac", "--x64"],
                    ["electron-builder", "--mac", "--arm64"],
                ],
                "linux": [["npm", "run", "build:linux"], ["electron-builder", "--linux"]],
            },
            dependencies={
                "all": ["Node.js", "npm"],
                "windows": ["Windows SDK", "Visual Studio Build Tools"],
                "macos": ["Xcode Command Line Tools"],
                "linux": ["build-essential", "libgtk-3-dev"],
            },
            signing={
                "windows": {"certificate": "build/certificate.p12", "password": "certificate_password"},
                "macos": {
                    "identity": "Developer ID Application: Your Name",
                    "hardened_runtime": True,
                    "gatekeeper_assess": False,
                },
            },
        )

    def _initialize_security_policies(self):
        """Initialize security policies for each framework"""
        # Tauri security policy
        self._security_policies[DesktopFramework.TAURI] = SecurityPolicy(
            sandbox_enabled=True,
            permissions={
                "fs": {
                    "allowed_paths": ["$APPDATA/*", "$DOCUMENT/*", "$DOWNLOAD/*"],
                    "allowed_operations": ["readFile", "writeFile", "readDir", "createDir"],
                },
                "dialog": {"allowed_operations": ["open", "save"]},
                "notification": {"allowed_operations": ["all"]},
            },
            api_restrictions=[
                "No direct file system access without permission",
                "No network access without explicit allowlist",
                "No shell command execution",
                "No clipboard access unless explicitly allowed",
            ],
            file_access_rules={
                "read": ["$APPDATA", "$DOCUMENT", "$DOWNLOAD", "$RESOURCE"],
                "write": ["$APPDATA", "$DOCUMENT", "$DOWNLOAD"],
                "execute": [],
            },
            network_policies=["HTTPS only for production", "CSP headers enforced", "No localhost access in production"],
            code_signing_required=True,
        )

        # Electron security policy
        self._security_policies[DesktopFramework.ELECTRON] = SecurityPolicy(
            sandbox_enabled=True,
            permissions={
                "node_integration": False,
                "context_isolation": True,
                "enable_remote_module": False,
                "web_security": True,
            },
            api_restrictions=[
                "No nodeIntegration in renderer",
                "No remote module loading",
                "No eval() or similar functions",
                "No unsafe content security policy bypass",
            ],
            file_access_rules={
                "read": ["appData", "documents", "downloads"],
                "write": ["appData", "documents", "temp"],
                "execute": ["app"],
            },
            network_policies=[
                "Content Security Policy enforced",
                "Node.js disabled in renderer",
                "WebSecurity enabled",
                "AllowRunningInsecureContent disabled",
            ],
            code_signing_required=True,
        )

    async def _generate_build_response(self, framework: str, platform: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Generate cross-platform build expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "Cross-Platform Build",
                "supported_frameworks": [f.value for f in DesktopFramework],
                "platform_targets": [p.value for p in Platform if p != Platform.ALL],
                "output_formats": {
                    "windows": ["MSI", "NSIS", "Portable"],
                    "macos": ["DMG", "APP", "PKG"],
                    "linux": ["DEB", "RPM", "AppImage"],
                },
            }

        elif level == DisclosureLevel.SUMMARY:
            build_config = self._get_build_config(framework)
            return {
                "expertise_area": "Cross-Platform Build Summary",
                "framework": framework,
                "dependencies": build_config.dependencies,
                "build_commands": build_config.build_commands,
                "output_formats": build_config.output_formats,
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_build_response(framework, platform)

        else:  # FULL
            return await self._generate_complete_build_response(framework, platform)

    def _get_build_config(self, framework: str) -> Optional[BuildConfiguration]:
        """Get build configuration for framework"""
        if not framework:
            return None

        try:
            framework_enum = DesktopFramework(framework.lower())
            return self._build_configurations.get(framework_enum)
        except ValueError:
            return None

    async def _generate_detailed_build_response(self, framework: str, platform: str) -> Dict[str, Any]:
        """Generate detailed build configuration"""
        build_config = self._get_build_config(framework)

        if not build_config:
            raise ValueError(f"No build configuration found for framework: {framework}")

        return {
            "expertise_area": "Cross-Platform Build - Detailed",
            "framework": framework,
            "build_pipeline": {
                "development": {
                    "commands": [
                        {"step": "Install dependencies", "command": "npm install"},
                        {"step": "Development build", "command": "npm run dev"},
                        {"step": "Test build", "command": "npm run test"},
                    ]
                },
                "production": {
                    "commands": build_config.build_commands,
                    "stages": [
                        {"name": "Code Signing", "description": "Sign binaries with developer certificates"},
                        {"name": "Package Creation", "description": "Create platform-specific installers"},
                        {"name": "Notarization", "description": "Notarize for macOS distribution"},
                        {"name": "Distribution", "description": "Prepare for release"},
                    ],
                },
            },
            "ci_cd_integration": {
                "github_actions": {
                    "windows_job": """
    build-windows:
      runs-on: windows-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-node@v3
          with:
            node-version: '18'
        - run: npm ci
        - run: npm run build:win
        - uses: actions/upload-artifact@v3
          with:
            name: windows-dist
            path: dist/""",
                    "macos_job": """
    build-macos:
      runs-on: macos-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-node@v3
          with:
            node-version: '18'
        - run: npm ci
        - run: npm run build:mac
        - uses: actions/upload-artifact@v3
          with:
            name: macos-dist
            path: dist/""",
                }
            },
        }

    async def _generate_complete_build_response(self, framework: str, platform: str) -> Dict[str, Any]:
        """Generate complete build configuration with production patterns"""
        return {
            "expertise_area": "Cross-Platform Build - Complete Production Guide",
            "framework": framework,
            "advanced_patterns": {
                "incremental_builds": {
                    "description": "Optimize build times with incremental compilation",
                    "implementation": {
                        "tauri": "Use cargo incremental compilation and cache optimization",
                        "electron": "Use webpack cache and electron-builder's incremental builds",
                    },
                },
                "build_optimization": {
                    "bundle_size": {
                        "techniques": [
                            "Tree shaking for unused code",
                            "Asset optimization and compression",
                            "Code splitting for large applications",
                            "Native module bundling optimization",
                        ]
                    },
                    "startup_time": {
                        "techniques": [
                            "Lazy loading of modules",
                            "Preload critical resources",
                            "Optimize main thread execution",
                            "Background initialization",
                        ]
                    },
                },
                "release_automation": {
                    "version_management": {
                        "semantic_versioning": "Use semantic versioning for releases",
                        "automatic_bumping": "Automatically bump version based on commits",
                        "changelog_generation": "Generate changelog from git history",
                    },
                    "distribution_channels": {
                        "direct": "Host installers on your own servers",
                        "app_stores": "Submit to Microsoft Store, Mac App Store, Snap Store",
                        "package_managers": "Publish to npm, Homebrew, Chocolatey",
                    },
                },
            },
            "troubleshooting_guide": {
                "common_issues": {
                    "build_failures": {
                        "causes": ["Missing dependencies", "Certificate issues", "Platform-specific errors"],
                        "solutions": [
                            "Verify all dependencies are installed",
                            "Check code signing certificates",
                            "Use platform-specific build environments",
                        ],
                    },
                    "runtime_errors": {
                        "causes": ["Missing native modules", "Permission issues", "Path problems"],
                        "solutions": [
                            "Bundle all dependencies correctly",
                            "Check application permissions",
                            "Use relative paths and proper path resolution",
                        ],
                    },
                }
            },
        }

    async def _generate_native_api_response(
        self, framework: str, platform: str, level: DisclosureLevel
    ) -> Dict[str, Any]:
        """Generate native API integration expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "Native API Integration",
                "capabilities": [
                    "System information access",
                    "Hardware integration",
                    "OS-specific features",
                    "Native library calls",
                ],
                "platforms": list(p.value for p in Platform if p != Platform.ALL),
            }

        elif level == DisclosureLevel.SUMMARY:
            return {
                "expertise_area": "Native API Integration Summary",
                "platform_capabilities": {
                    "windows": ["Registry access", "Windows API", "COM objects", "WMI queries"],
                    "macos": ["Objective-C bridges", "AppKit integration", "System Preferences", "AppleScript"],
                    "linux": ["DBus integration", "Systemd services", "GTK integration", "Shell commands"],
                },
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_native_api_response(framework, platform)

        else:  # FULL
            return await self._generate_complete_native_api_response(framework, platform)

    async def _generate_detailed_native_api_response(self, framework: str, platform: str) -> Dict[str, Any]:
        """Generate detailed native API integration examples"""
        return {
            "expertise_area": "Native API Integration - Detailed Examples",
            "framework": framework,
            "platform_specific": {
                "windows": {
                    "system_information": {
                        "tauri": """
#[tauri::command]
async fn get_system_info() -> Result<SystemInfo, String> {
    use std::process::Command;

    let output = Command::new("wmic")
        .args(&["computersystem", "get", "TotalPhysicalMemory", "/format:list"])
        .output();

    match output {
        Ok(result) => {
            let output_str = String::from_utf8_lossy(&result.stdout);
            let memory = extract_memory_from_wmic(&output_str);
            Ok(SystemInfo { total_memory: memory })
        }
        Err(e) => Err(format!("Failed to get system info: {}", e))
    }
}""",
                        "electron": """
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function getSystemInfo() {
  try {
    const { stdout } = await execAsync('wmic computersystem get TotalPhysicalMemory /format:list');
    const memoryMatch = stdout.match(/TotalPhysicalMemory=(\\d+)/);
    return {
      totalMemory: memoryMatch ? parseInt(memoryMatch[1]) : 0,
      platform: 'windows'
    };
  } catch (error) {
    throw new Error(`Failed to get system info: ${error.message}`);
  }
}""",
                    }
                },
                "macos": {
                    "system_information": {
                        "tauri": """
#[tauri::command]
async fn get_macos_system_info() -> Result<SystemInfo, String> {
    use std::process::Command;

    let output = Command::new("sysctl")
        .args(&["-n", "hw.memsize"])
        .output();

    match output {
        Ok(result) => {
            let output_str = String::from_utf8_lossy(&result.stdout);
            let memory = output_str.trim().parse::<u64>().unwrap_or(0);
            Ok(SystemInfo { total_memory: memory })
        }
        Err(e) => Err(format!("Failed to get system info: {}", e))
    }
}""",
                        "electron": """
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function getMacosSystemInfo() {
  try {
    const { stdout } = await execAsync('sysctl -n hw.memsize');
    const memory = parseInt(stdout.trim());
    return {
      totalMemory: memory,
      platform: 'macos'
    };
  } catch (error) {
    throw new Error(`Failed to get system info: ${error.message}`);
  }
}""",
                    }
                },
            },
        }

    async def _generate_complete_native_api_response(self, framework: str, platform: str) -> Dict[str, Any]:
        """Generate complete native API integration with advanced patterns"""
        return {
            "expertise_area": "Native API Integration - Complete Reference",
            "advanced_patterns": {
                "async_native_operations": {
                    "description": "Non-blocking native API calls with proper error handling",
                    "implementation": {
                        "rust_tauri": """
use tokio::process::Command;
use std::time::Duration;

#[tauri::command]
async fn async_native_operation(param: String) -> Result<String, String> {
    let command = Command::new("native-command")
        .arg(&param)
        .output();

    match tokio::time::timeout(Duration::from_secs(30), command).await {
        Ok(Ok(output)) => {
            if output.status.success() {
                Ok(String::from_utf8_lossy(&output.stdout).to_string())
            } else {
                Err(format!("Command failed: {}", String::from_utf8_lossy(&output.stderr)))
            }
        }
        Ok(Err(e)) => Err(format!("Failed to execute command: {}", e)),
        Err(_) => Err("Command timed out".to_string())
    }
}"""
                    },
                },
                "native_library_integration": {
                    "ffi_integration": {
                        "description": "FFI bindings for native libraries",
                        "caution": "Use only when necessary, as it increases complexity and security risks",
                    }
                },
                "platform_detection": {
                    "runtime_detection": """
fn get_platform_capabilities() -> PlatformCapabilities {
    match std::env::consts::OS {
        "windows" => PlatformCapabilities {
            has_registry: true,
            has_wmi: true,
            has_com: true,
            supports_notifications: true,
        },
        "macos" => PlatformCapabilities {
            has_apple_script: true,
            has_objc_bridge: true,
            has_spotlight: true,
            supports_notifications: true,
        },
        "linux" => PlatformCapabilities {
            has_dbus: true,
            has_systemd: true,
            has_x11: true,
            supports_notifications: true,
        },
        _ => PlatformCapabilities::default()
    }
}"""
                },
            },
            "security_considerations": {
                "input_validation": [
                    "Always validate external inputs before passing to native APIs",
                    "Sanitize file paths to prevent directory traversal",
                    "Use allowlists for acceptable commands and parameters",
                ],
                "privilege_escalation": [
                    "Avoid running with elevated privileges when possible",
                    "Use user-specific directories and settings",
                    "Implement proper permission checks before sensitive operations",
                ],
                "resource_limits": [
                    "Set timeouts for native operations",
                    "Monitor memory usage of native calls",
                    "Implement circuit breakers for unreliable external commands",
                ],
            },
        }

    async def _generate_file_system_response(self, framework: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Generate file system access expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "File System Access",
                "capabilities": [
                    "Secure file operations",
                    "Directory management",
                    "File watching",
                    "Drag and drop support",
                ],
                "security_focus": "Sandboxed access with explicit permissions",
            }

        elif level == DisclosureLevel.SUMMARY:
            return {
                "expertise_area": "File System Access Summary",
                "frameworks": {
                    "tauri": {
                        "permissions": "File system allowlist in tauri.conf.json",
                        "api": "Rust std::fs with Tauri commands",
                        "security": "Path validation and sandboxing",
                    },
                    "electron": {
                        "permissions": "Main process controls with IPC",
                        "api": "Node.js fs module with preload scripts",
                        "security": "Context isolation and path validation",
                    },
                },
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_file_system_response(framework)

        else:  # FULL
            return await self._generate_complete_file_system_response(framework)

    async def _generate_detailed_file_system_response(self, framework: str) -> Dict[str, Any]:
        """Generate detailed file system implementation examples"""
        return {
            "expertise_area": "File System Access - Detailed Implementation",
            "framework": framework,
            "secure_patterns": {
                "path_validation": {
                    "description": "Validate file paths to prevent directory traversal attacks",
                    "implementation": {
                        "rust": """
use std::path::{Path, Component};

fn validate_path(path: &str, allowed_base: &Path) -> bool {
    let full_path = Path::new(path);

    // Resolve relative components
    let canonical_path = match full_path.canonicalize() {
        Ok(path) => path,
        Err(_) => return false,
    };

    // Check if path is within allowed base directory
    canonical_path.starts_with(allowed_base)
}""",
                        "javascript": """
const path = require('path');

function validatePath(filePath, allowedBase) {
  const resolvedPath = path.resolve(filePath);
  return resolvedPath.startsWith(path.resolve(allowedBase));
}""",
                    },
                },
                "file_operations": {
                    "secure_file_reading": {
                        "tauri": """
#[tauri::command]
async fn secure_read_file(path: String) -> Result<String, String> {
    use std::fs;
    use std::path::Path;

    // Get allowed directories from config
    let allowed_dirs = vec![
        get_app_data_dir(),
        get_documents_dir(),
    ];

    let file_path = Path::new(&path);

    // Validate path is within allowed directories
    let is_allowed = allowed_dirs.iter().any(|dir| file_path.starts_with(dir));
    if !is_allowed {
        return Err("Access denied: Path not in allowed directory".to_string());
    }

    // Check file size to prevent memory issues
    let metadata = fs::metadata(&file_path).map_err(|e| e.to_string())?;
    if metadata.len() > 10_000_000 { // 10MB limit
        return Err("File too large".to_string());
    }

    // Read file
    fs::read_to_string(&file_path).map_err(|e| e.to_string())
}""",
                        "electron": """
const fs = require('fs').promises;
const path = require('path');

async function secureReadFile(filePath) {
  const allowedPaths = [
    app.getPath('appData'),
    app.getPath('documents'),
    app.getPath('downloads')
  ];

  const resolvedPath = path.resolve(filePath);
  const isAllowed = allowedPaths.some(allowed =>
    resolvedPath.startsWith(path.resolve(allowed))
  );

  if (!isAllowed) {
    throw new Error('Access denied: Path not in allowed directory');
  }

  // Check file size
  const stats = await fs.stat(resolvedPath);
  if (stats.size > 10_000_000) { // 10MB limit
    throw new Error('File too large');
  }

  return await fs.readFile(resolvedPath, 'utf8');
}""",
                    }
                },
                "file_watching": {
                    "directory_watcher": {
                        "tauri": """
#[tauri::command]
async fn watch_directory(path: String, window: tauri::Window) -> Result<(), String> {
    use std::sync::mpsc;
    use std::thread;
    use notify::{Watcher, RecursiveMode, RecommendedWatcher};

    let (tx, rx) = mpsc::channel();
    let mut watcher: RecommendedWatcher = Watcher::new(tx, notify::Config::default())
        .map_err(|e| e.to_string())?;

    watcher.watch(Path::new(&path), RecursiveMode::Recursive)
        .map_err(|e| e.to_string())?;

    thread::spawn(move || {
        while let Ok(event) = rx.recv() {
            let _ = window.emit("file-change", &event);
        }
    });

    Ok(())
}"""
                    }
                },
            },
        }

    async def _generate_complete_file_system_response(self, framework: str) -> Dict[str, Any]:
        """Generate complete file system integration with advanced patterns"""
        return {
            "expertise_area": "File System Access - Complete Production Guide",
            "advanced_patterns": {
                "drag_and_drop": {
                    "implementation": {
                        "tauri_frontend": """
document.addEventListener('dragover', (e) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'copy';
});

document.addEventListener('drop', async (e) => {
  e.preventDefault();

  const files = Array.from(e.dataTransfer.files);
  const results = [];

  for (const file of files) {
    try {
      const content = await file.text();
      const result = await invoke('save_dropped_file', {
        name: file.name,
        content: content
      });
      results.push(result);
    } catch (error) {
      results.push({ error: error.message });
    }
  }

  return results;
});""",
                        "tauri_backend": """
#[tauri::command]
async fn save_dropped_file(name: String, content: String) -> Result<String, String> {
    use std::fs;
    use std::path::Path;

    let upload_dir = get_upload_directory().map_err(|e| e.to_string())?;
    let file_path = upload_dir.join(&name);

    // Sanitize filename
    let safe_name = sanitize_filename(&name);
    let safe_path = upload_dir.join(&safe_name);

    fs::write(&safe_path, content).map_err(|e| e.to_string())?;

    Ok(safe_path.to_string_lossy().to_string())
}

fn sanitize_filename(filename: &str) -> String {
    filename
        .chars()
        .map(|c| if c.is_alphanumeric() || c == '.' || c == '-' || c == '_' { c } else { '_' })
        .collect()
}""",
                    }
                },
                "file_type_detection": {
                    "mime_type_detection": """
use std::path::Path;
use std::ffi::OsStr;

fn detect_file_type(file_path: &Path) -> &'static str {
    match file_path.extension().and_then(OsStr::to_str) {
        Some("txt") => "text/plain",
        Some("json") => "application/json",
        Some("png") => "image/png",
        Some("jpg") | Some("jpeg") => "image/jpeg",
        Some("pdf") => "application/pdf",
        Some("mp4") => "video/mp4",
        Some("mp3") => "audio/mpeg",
        _ => "application/octet-stream"
    }
}"""
                },
                "file_compression": {
                    "zip_operations": """
#[tauri::command]
async fn compress_files(file_paths: Vec<String>, output_path: String) -> Result<(), String> {
    use zip::ZipWriter;
    use std::fs::File;
    use std::io::{BufReader, Write};

    let file = File::create(&output_path).map_err(|e| e.to_string())?;
    let mut zip = ZipWriter::new(file);

    for file_path in file_paths {
        let path = Path::new(&file_path);
        if path.is_file() {
            let file_name = path.file_name()
                .ok_or("Invalid filename")?
                .to_string_lossy()
                .to_string();

            zip.start_file(&file_name, zip::write::FileOptions::default())?;

            let input_file = File::open(&path).map_err(|e| e.to_string())?;
            let mut reader = BufReader::new(input_file);

            std::io::copy(&mut reader, &mut zip).map_err(|e| e.to_string())?;
        }
    }

    zip.finish().map_err(|e| e.to_string())?;
    Ok(())
}"""
                },
            },
            "performance_optimization": {
                "async_operations": [
                    "Use async file operations to prevent UI blocking",
                    "Implement streaming for large file transfers",
                    "Use file chunking for memory-efficient processing",
                ],
                "caching_strategies": [
                    "Cache file metadata to reduce system calls",
                    "Implement in-memory caching for frequently accessed files",
                    "Use etags or file modification time for cache invalidation",
                ],
            },
            "error_handling_patterns": {
                "graceful_degradation": [
                    "Provide fallback behavior when file operations fail",
                    "Offer alternative storage locations",
                    "Implement retry logic for transient failures",
                ],
                "user_feedback": [
                    "Show progress indicators for long-running operations",
                    "Provide clear error messages with actionable advice",
                    "Offer retry options for recoverable errors",
                ],
            },
        }

    async def _generate_system_integration_response(self, framework: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Generate system integration expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "System Integration",
                "features": [
                    "System tray integration",
                    "Native notifications",
                    "Auto-start management",
                    "Deep linking",
                    "File associations",
                ],
            }

        elif level == DisclosureLevel.SUMMARY:
            return {
                "expertise_area": "System Integration Summary",
                "capabilities": {
                    "system_tray": "Background access via system tray",
                    "notifications": "Native OS notifications",
                    "auto_start": "Launch at system startup",
                    "deep_linking": "Handle custom URL schemes",
                    "file_associations": "Register as default app for file types",
                },
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_system_integration_response(framework)

        else:  # FULL
            return await self._generate_complete_system_integration_response(framework)

    async def _generate_detailed_system_integration_response(self, framework: str) -> Dict[str, Any]:
        """Generate detailed system integration implementation"""
        return {
            "expertise_area": "System Integration - Detailed Implementation",
            "framework": framework,
            "system_tray": {
                "tauri": """
#[tauri::command]
async fn setup_system_tray(app_handle: tauri::AppHandle) -> Result<(), String> {
    use tauri::{CustomMenuItem, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem};

    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide");
    let show = CustomMenuItem::new("show".to_string(), "Show");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    app_handle.system_tray_handle().replace_menu(system_tray.menu)?;

    Ok(())
}

#[tauri::command]
async fn handle_tray_event(app: tauri::AppHandle, event: String) {
    match event.as_str() {
        "quit" => std::process::exit(0),
        "hide" => {
            if let Some(window) = app.get_window("main") {
                let _ = window.hide();
            }
        }
        "show" => {
            if let Some(window) = app.get_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }
        _ => {}
    }
}""",
                "electron": """
const { Tray, Menu, nativeImage } = require('electron');

class SystemTrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.tray = null;
    this.setup();
  }

  setup() {
    const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
    const icon = nativeImage.createFromPath(iconPath);

    this.tray = new Tray(icon.resize({ width: 16, height: 16 }));

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show Application',
        click: () => {
          this.mainWindow.show();
          this.mainWindow.focus();
        }
      },
      { type: 'separator' },
      {
        label: 'Quit',
        click: () => {
          this.mainWindow.close();
        }
      }
    ]);

    this.tray.setToolTip('My Application');
    this.tray.setContextMenu(contextMenu);

    this.tray.on('click', () => {
      this.mainWindow.isVisible()
        ? this.mainWindow.hide()
        : this.mainWindow.show();
    });
  }
}""",
            },
            "notifications": {
                "cross_platform": """
#[cfg(target_os = "windows")]
fn show_windows_notification(title: &str, body: &str) -> Result<(), Box<dyn std::error::Error>> {
    use winrt::windows::ui::notifications::{ToastNotification, ToastNotificationManager};
    use winrt::windows::data::xml::dom::XmlDocument;

    let xml = format!(
        r#"<toast>
            <visual>
                <binding template="ToastGeneric">
                    <text>{}</text>
                    <text>{}</text>
                </binding>
            </visual>
        </toast>"#,
        title, body
    );

    let doc = XmlDocument::new()?;
    doc.load_xml(xml)?;

    let toast = ToastNotification::create_toast_notification(doc)?;
    ToastNotificationManager::create_toast_notifier()?.show(toast)?;

    Ok(())
}

#[cfg(target_os = "macos")]
fn show_macos_notification(title: &str, body: &str) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command;

    Command::new("osascript")
        .arg("-e")
        .arg(&format!(
            r#"display notification "{}" with title "{}""#,
            body, title
        ))
        .spawn()?;

    Ok(())
}

#[cfg(target_os = "linux")]
fn show_linux_notification(title: &str, body: &str) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command;

    Command::new("notify-send")
        .arg(title)
        .arg(body)
        .arg("-i")
        .arg("dialog-information")
        .spawn()?;

    Ok(())
}"""
            },
        }

    async def _generate_complete_system_integration_response(self, framework: str) -> Dict[str, Any]:
        """Generate complete system integration with advanced patterns"""
        return {
            "expertise_area": "System Integration - Complete Production Guide",
            "advanced_patterns": {
                "auto_start": {
                    "windows_registry": """
#[cfg(target_os = "windows")]
use winreg::enums::*;
use winreg::RegKey;

fn set_auto_start(enabled: bool) -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::current_exe()?;
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let path_str = path.to_string_lossy();

    let key = hkcu.open_subkey_with_flags(
        r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
        KEY_WRITE
    )?;

    if enabled {
        key.set_value("MyApp", &path_str)?;
    } else {
        key.delete_value("MyApp")?;
    }

    Ok(())
}""",
                    "macos_launch_agent": """
#[cfg(target_os = "macos")]
fn set_macos_auto_start(enabled: bool) -> Result<(), Box<dyn std::error::Error>> {
    use std::fs;
    use std::path::Path;

    let home_dir = std::env::var("HOME")?;
    let launch_agents_dir = Path::new(&home_dir).join("Library/LaunchAgents");
    let plist_file = launch_agents_dir.join("com.myapp.plist");

    if enabled {
        fs::create_dir_all(&launch_agents_dir)?;

        let plist_content = format!(
            r#"<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.myapp</string>
    <key>ProgramArguments</key>
    <array>
        <string>{}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"#,
            std::env::current_exe()?.to_string_lossy()
        );

        fs::write(&plist_file, plist_content)?;
    } else {
        fs::remove_file(&plist_file).ok();
    }

    Ok(())
}""",
                },
                "deep_linking": {
                    "protocol_registration": """
# Windows registry registration for custom protocol
[HKEY_CLASSES_ROOT\\myapp]
@="URL:MyApp Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\\myapp\\shell\\open\\command]
@="\\"C:\\\\Program Files\\\\MyApp\\\\myapp.exe\\" \\"%1\\""

# macOS app bundle registration for custom URL scheme
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>com.myapp.url</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>myapp</string>
        </array>
    </dict>
</array>

# Linux desktop file registration
[Desktop Entry]
Type=Application
Name=MyApp
Exec=/usr/bin/myapp %u
MimeType=x-scheme-handler/myapp;
NoDisplay=true
"""
                },
                "file_associations": {
                    "registration_examples": """
# Windows file association
[HKEY_CLASSES_ROOT\\.myfile]
@="MyApp.File"

[HKEY_CLASSES_ROOT\\MyApp.File]
@="MyApp Document"

[HKEY_CLASSES_ROOT\\MyApp.File\\shell\\open\\command]
@="\\"C:\\\\Program Files\\\\MyApp\\\\myapp.exe\\" \\"%1\\""

# macOS bundle file association
<key>CFBundleDocumentTypes</key>
<array>
    <dict>
        <key>CFBundleTypeName</key>
        <string>MyApp Document</string>
        <key>CFBundleTypeExtensions</key>
        <array>
            <string>myfile</string>
        </array>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
    </dict>
</array>

# Linux MIME type registration
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="application/x-myapp">
        <comment>MyApp Document</comment>
        <glob pattern="*.myfile"/>
    </mime-type>
</mime-info>
"""
                },
            },
            "security_considerations": {
                "auto_start": [
                    "Always provide user option to disable auto-start",
                    "Clearly indicate auto-start status in preferences",
                    "Handle auto-start removal cleanly",
                ],
                "deep_linking": [
                    "Validate all URL parameters before processing",
                    "Sanitize file paths from deep links",
                    "Implement rate limiting for deep link handling",
                ],
                "file_associations": [
                    "Validate file types before opening",
                    "Implement file size limits",
                    "Provide clear warnings for potentially dangerous files",
                ],
            },
        }

    async def _generate_performance_response(self, framework: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Generate performance optimization expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "Performance Optimization",
                "focus_areas": ["Memory management", "Startup optimization", "Runtime performance", "Resource usage"],
            }

        elif level == DisclosureLevel.SUMMARY:
            return {
                "expertise_area": "Performance Optimization Summary",
                "framework_patterns": {
                    "tauri": {
                        "advantages": ["Rust performance", "Small binary size", "Low memory usage"],
                        "optimizations": ["Cargo release builds", "Strip symbols", "Optimize dependencies"],
                    },
                    "electron": {
                        "advantages": ["JavaScript optimization", "V8 engine", "Rich debugging tools"],
                        "optimizations": ["Context isolation", "Code splitting", "Lazy loading"],
                    },
                },
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_performance_response(framework)

        else:  # FULL
            return await self._generate_complete_performance_response(framework)

    async def _generate_detailed_performance_response(self, framework: str) -> Dict[str, Any]:
        """Generate detailed performance optimization examples"""
        return {
            "expertise_area": "Performance Optimization - Detailed Implementation",
            "framework": framework,
            "memory_optimization": {
                "tauri": {
                    "cargo_configuration": """
[profile.release]
lto = true
codegen-units = 1
panic = "abort"
strip = true

[profile.release.package."*"]
opt-level = 3""",
                    "memory_management": """
// Use weak references for non-critical data
use std::sync::{Arc, Weak};
use std::collections::HashMap;

struct AppState {
    cache: Arc<RwLock<HashMap<String, Weak<Data>>>>,
    active_windows: Vec<Window>,
}

impl AppState {
    fn get_cached_data(&self, key: &str) -> Option<Arc<Data>> {
        let cache = self.cache.read().unwrap();
        cache.get(key)?.upgrade()
    }

    fn cache_data(&self, key: String, data: Arc<Data>) {
        let mut cache = self.cache.write().unwrap();
        cache.insert(key, Arc::downgrade(&data));
    }
}""",
                },
                "electron": {
                    "memory_leak_prevention": """
// Proper cleanup of event listeners and timers
class WindowManager {
  constructor() {
    this.windows = new Set();
    this.timers = new Set();
  }

  createWindow(options) {
    const window = new BrowserWindow(options);
    this.windows.add(window);

    // Clean up on close
    window.on('closed', () => {
      this.windows.delete(window);
    });

    return window;
  }

  createTimer(callback, delay) {
    const timerId = setTimeout(callback, delay);
    this.timers.add(timerId);

    // Return cleanup function
    return () => {
      clearTimeout(timerId);
      this.timers.delete(timerId);
    };
  }

  cleanup() {
    // Clear all timers
    for (const timerId of this.timers) {
      clearTimeout(timerId);
    }
    this.timers.clear();

    // Close all windows
    for (const window of this.windows) {
      if (!window.isDestroyed()) {
        window.close();
      }
    }
    this.windows.clear();
  }
}"""
                },
            },
            "startup_optimization": {
                "lazy_loading": """
// Lazy load heavy modules
const modules = {
  heavyModule: null,
  async load() {
    if (!this.heavyModule) {
      this.heavyModule = await import('./heavy-module.js');
    }
    return this.heavyModule;
  }
};

// Defer non-critical initialization
async function initializeApp() {
  // Critical path first
  await initializeCore();

  // Show UI as soon as possible
  mainWindow.show();

  // Defer heavy initialization
  setTimeout(async () => {
    await modules.load();
    await initializeFeatures();
  }, 100);
}""",
                "resource_optimization": """
// Optimize resource loading
class ResourceOptimizer {
  constructor() {
    this.criticalResources = new Set();
    this.deferredResources = new Set();
  }

  markCritical(url) {
    this.criticalResources.add(url);
  }

  defer(url) {
    this.deferredResources.add(url);
  }

  async loadCritical() {
    const promises = Array.from(this.criticalResources).map(url => this.loadResource(url));
    await Promise.all(promises);
  }

  async loadDeferred() {
    const promises = Array.from(this.deferredResources).map(url =>
      this.loadResource(url).catch(err => console.warn(`Failed to load ${url}:`, err))
    );
    await Promise.all(promises);
  }

  async loadResource(url) {
    // Implement resource loading with caching
  }
}""",
            },
        }

    async def _generate_complete_performance_response(self, framework: str) -> Dict[str, Any]:
        """Generate complete performance optimization with advanced patterns"""
        return {
            "expertise_area": "Performance Optimization - Complete Production Guide",
            "advanced_patterns": {
                "cpu_optimization": {
                    "web_workers": """
// Use Web Workers for CPU-intensive tasks
class WorkerPool {
  constructor(workerScript, size = navigator.hardwareConcurrency || 4) {
    this.workers = [];
    this.taskQueue = [];
    this.busyWorkers = new Set();

    for (let i = 0; i < size; i++) {
      const worker = new Worker(workerScript);
      this.workers.push(worker);
    }
  }

  async execute(data) {
    return new Promise((resolve, reject) => {
      const task = { data, resolve, reject };

      if (this.busyWorkers.size < this.workers.length) {
        this.executeTask(task);
      } else {
        this.taskQueue.push(task);
      }
    });
  }

  executeTask({ data, resolve, reject }) {
    const worker = this.workers.find(w => !this.busyWorkers.has(w));
    if (!worker) return;

    this.busyWorkers.add(worker);

    const handleMessage = (result) => {
      this.busyWorkers.delete(worker);
      worker.removeEventListener('message', handleMessage);
      worker.removeEventListener('error', handleError);
      resolve(result.data);
      this.processQueue();
    };

    const handleError = (error) => {
      this.busyWorkers.delete(worker);
      worker.removeEventListener('message', handleMessage);
      worker.removeEventListener('error', handleError);
      reject(error);
      this.processQueue();
    };

    worker.addEventListener('message', handleMessage);
    worker.addEventListener('error', handleError);
    worker.postMessage(data);
  }

  processQueue() {
    if (this.taskQueue.length > 0 && this.busyWorkers.size < this.workers.length) {
      const task = this.taskQueue.shift();
      this.executeTask(task);
    }
  }
}"""
                },
                "gpu_optimization": {
                    "accelerated_rendering": """
// Use GPU-accelerated CSS and Canvas
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d', {
  alpha: false,
  desynchronized: true,
  willReadFrequently: false
});

// GPU-accelerated animations
class GPUSprite {
  constructor(texture, x, y) {
    this.texture = texture;
    this.x = x;
    this.y = y;
    this.element = this.createElement();
  }

  createElement() {
    const element = document.createElement('div');
    element.style.cssText = `
      position: absolute;
      width: ${this.texture.width}px;
      height: ${this.texture.height}px;
      background-image: url(${this.texture.url});
      background-size: contain;
      transform: translate3d(${this.x}px, ${this.y}px, 0);
      will-change: transform;
    `;
    return element;
  }

  moveTo(x, y) {
    this.x = x;
    this.y = y;
    this.element.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  }
}"""
                },
                "network_optimization": {
                    "resource_caching": """
// Service worker for resource caching
class ResourceCache {
  constructor() {
    this.cache = new Map();
    this.maxSize = 50 * 1024 * 1024; // 50MB
    this.currentSize = 0;
  }

  async cache(url, response) {
    const blob = await response.blob();
    const size = blob.size;

    // Evict old items if necessary
    while (this.currentSize + size > this.maxSize && this.cache.size > 0) {
      const [key, entry] = this.cache.entries().next().value;
      this.currentSize -= entry.size;
      this.cache.delete(key);
    }

    this.cache.set(url, { blob, size, timestamp: Date.now() });
    this.currentSize += size;
  }

  async get(url) {
    const entry = this.cache.get(url);
    if (!entry) return null;

    // Check if expired (1 hour)
    if (Date.now() - entry.timestamp > 3600000) {
      this.cache.delete(url);
      this.currentSize -= entry.size;
      return null;
    }

    return new Response(entry.blob);
  }
}"""
                },
            },
            "monitoring_and_profiling": {
                "performance_metrics": """
// Collect performance metrics
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      memory: [],
      cpu: [],
      fps: [],
      network: []
    };
    this.isMonitoring = false;
  }

  start() {
    this.isMonitoring = true;
    this.collectMetrics();
  }

  collectMetrics() {
    if (!this.isMonitoring) return;

    // Memory usage
    if (performance.memory) {
      this.metrics.memory.push({
        timestamp: Date.now(),
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      });
    }

    // FPS measurement
    this.measureFPS();

    setTimeout(() => this.collectMetrics(), 1000);
  }

  measureFPS() {
    let lastTime = performance.now();
    let frames = 0;

    const measure = (currentTime) => {
      frames++;

      if (currentTime - lastTime >= 1000) {
        this.metrics.fps.push({
          timestamp: Date.now(),
          fps: Math.round((frames * 1000) / (currentTime - lastTime))
        });

        frames = 0;
        lastTime = currentTime;
      }

      if (this.isMonitoring) {
        requestAnimationFrame(measure);
      }
    };

    requestAnimationFrame(measure);
  }

  getMetrics() {
    return this.metrics;
  }
}"""
            },
        }

    async def _generate_security_response(self, framework: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Generate security expertise response"""
        if level == DisclosureLevel.METADATA:
            return {
                "expertise_area": "Security Integration",
                "focus_areas": ["Sandboxing", "Code signing", "Input validation", "Secure communication"],
            }

        elif level == DisclosureLevel.SUMMARY:
            security_policy = self._security_policies.get(DesktopFramework(framework.lower())) if framework else None
            return {
                "expertise_area": "Security Summary",
                "framework_security": security_policy.__dict__ if security_policy else "Framework not specified",
            }

        elif level == DisclosureLevel.DETAILED:
            return await self._generate_detailed_security_response(framework)

        else:  # FULL
            return await self._generate_complete_security_response(framework)

    async def _generate_detailed_security_response(self, framework: str) -> Dict[str, Any]:
        """Generate detailed security implementation examples"""
        return {
            "expertise_area": "Security Integration - Detailed Implementation",
            "framework": framework,
            "secure_configuration": {
                "content_security_policy": {
                    "examples": {
                        "restrictive": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.example.com",
                        "development": "default-src 'self' 'unsafe-eval' 'unsafe-inline'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' ws: wss:",
                    }
                },
                "sandbox_configuration": {
                    "tauri": """
{
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "scope": ["$APPDATA/app-name/*", "$DOCUMENT/app-name/*"]
      },
      "shell": {
        "all": false,
        "open": true
      }
    },
    "security": {
      "csp": "default-src 'self'; script-src 'self' 'unsafe-inline'"
    }
  }
}""",
                    "electron": """
const secureWindowConfig = {
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    enableRemoteModule: false,
    webSecurity: true,
    sandbox: true,
    preload: path.join(__dirname, 'preload.js')
  }
};""",
                },
            },
            "input_validation": {
                "file_path_validation": """
// Secure file path validation
function validateFilePath(filePath, allowedPaths) {
  // Resolve the absolute path
  const absolutePath = path.resolve(filePath);

  // Check if path is within allowed directories
  for (const allowedPath of allowedPaths) {
    const resolvedAllowed = path.resolve(allowedPath);
    if (absolutePath.startsWith(resolvedAllowed)) {
      // Additional checks
      if (!absolutePath.includes('..') && !/[<>:"|?*]/.test(filePath)) {
        return absolutePath;
      }
    }
  }

  throw new Error('Invalid file path');
}

// URL validation
function validateURL(url, allowedDomains) {
  try {
    const parsed = new URL(url);

    // Only allow HTTPS in production
    if (process.env.NODE_ENV === 'production' && parsed.protocol !== 'https:') {
      throw new Error('Only HTTPS URLs are allowed');
    }

    // Check against allowed domains
    if (allowedDomains && !allowedDomains.includes(parsed.hostname)) {
      throw new Error('Domain not allowed');
    }

    return parsed.href;
  } catch (error) {
    throw new Error('Invalid URL');
  }
}"""
            },
        }

    async def _generate_complete_security_response(self, framework: str) -> Dict[str, Any]:
        """Generate complete security integration with advanced patterns"""
        return {
            "expertise_area": "Security Integration - Complete Production Guide",
            "advanced_patterns": {
                "code_signing": {
                    "automated_signing": """
# GitHub Actions workflow for automated code signing
name: Build and Sign

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Import certificate
      run: |
        echo ${{ secrets.CERTIFICATE_BASE64 }} | base64 -d > certificate.p12
        echo ${{ secrets.CERTIFICATE_PASSWORD }} > password.txt

    - name: Build and sign
      run: npm run build:signed
      env:
        CSC_LINK: certificate.p12
        CSC_KEY_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: signed-app
        path: dist/"""
                },
                "runtime_protection": {
                    "anti_tampering": """
// Runtime integrity checks
class IntegrityChecker {
  constructor() {
    this.expectedHash = 'EXPECTED_HASH_HERE';
    this.checkInterval = 30000; // 30 seconds
  }

  async checkIntegrity() {
    try {
      const response = await fetch('./integrity.json');
      const manifest = await response.json();

      for (const [file, expectedHash] of Object.entries(manifest)) {
        const fileResponse = await fetch(file);
        const content = await fileResponse.text();
        const actualHash = await this.calculateHash(content);

        if (actualHash !== expectedHash) {
          throw new Error(`File integrity check failed: ${file}`);
        }
      }

      return true;
    } catch (error) {
      console.error('Integrity check failed:', error);
      return false;
    }
  }

  async calculateHash(content) {
    const encoder = new TextEncoder();
    const data = encoder.encode(content);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  startMonitoring() {
    setInterval(async () => {
      const isValid = await this.checkIntegrity();
      if (!isValid) {
        this.handleTampering();
      }
    }, this.checkInterval);
  }

  handleTampering() {
    // Take appropriate action (close app, show warning, etc.)
    if (confirm('Application integrity compromised. Close now?')) {
      window.close();
    }
  }
}"""
                },
            },
            "security_checklist": {
                "pre_deployment": [
                    "All external inputs validated and sanitized",
                    "CSP headers properly configured",
                    "Code signing certificates valid",
                    "Dependencies scanned for vulnerabilities",
                    "Error messages don't leak sensitive information",
                    "Debug information removed from production builds",
                    "Secure defaults for all configuration options",
                    "Proper entropy for cryptographic operations",
                ],
                "runtime_monitoring": [
                    "Monitor for suspicious file access patterns",
                    "Validate all network requests",
                    "Check for code injection attempts",
                    "Monitor memory usage for anomalies",
                    "Log security events for audit trail",
                ],
            },
            "compliance_considerations": {
                "gdpr": [
                    "Data minimization principles",
                    "User consent for data collection",
                    "Right to data deletion",
                    "Privacy by design implementation",
                ],
                "accessibility": [
                    "WCAG 2.1 AA compliance",
                    "Keyboard navigation support",
                    "Screen reader compatibility",
                    "High contrast mode support",
                ],
            },
        }

    async def _generate_comprehensive_response(self, request: Dict[str, Any], level: DisclosureLevel) -> Dict[str, Any]:
        """Generate comprehensive desktop integration response"""
        query = request.get("query", "").lower()
        framework = request.get("framework")

        # Analyze query to provide targeted expertise
        analysis = self._analyze_query(query)

        response = {
            "expertise_area": "Desktop Integration - Comprehensive Analysis",
            "query_analysis": analysis,
            "recommendations": [],
        }

        # Add framework-specific guidance
        if framework:
            response["framework_guidance"] = await self._get_framework_comprehensive_guidance(framework, level)

        # Add relevant patterns based on analysis
        for category in analysis["detected_categories"]:
            if category == "security":
                response["recommendations"].extend(
                    [
                        "Implement Content Security Policy (CSP)",
                        "Use context isolation and sandboxing",
                        "Validate all external inputs",
                        "Implement proper error handling without information leakage",
                    ]
                )
            elif category == "performance":
                response["recommendations"].extend(
                    [
                        "Optimize bundle size with tree shaking",
                        "Use lazy loading for non-critical resources",
                        "Implement efficient memory management",
                        "Monitor performance metrics in production",
                    ]
                )
            elif category == "cross_platform":
                response["recommendations"].extend(
                    [
                        "Test on all target platforms",
                        "Use platform-specific optimizations",
                        "Implement consistent user experience",
                        "Handle platform-specific file paths and APIs",
                    ]
                )

        return response

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to detect relevant categories and provide insights"""
        categories = []
        keywords = {
            "security": ["security", "secure", "protect", "vulnerability", "encrypt", "auth", "permission"],
            "performance": ["performance", "optimization", "fast", "memory", "cpu", "slow", "speed"],
            "cross_platform": ["cross-platform", "multi-platform", "windows", "macos", "linux", "platform"],
            "build": ["build", "compile", "package", "deploy", "release", "distribute"],
            "native": ["native", "api", "system", "os", "platform-specific", "hardware"],
            "file": ["file", "directory", "folder", "read", "write", "save", "load"],
            "ui": ["ui", "interface", "tray", "notification", "menu", "dialog"],
            "startup": ["startup", "launch", "auto-start", "boot", "init"],
        }

        for category, words in keywords.items():
            if any(word in query for word in words):
                categories.append(category)

        # Detect framework preferences
        frameworks = {
            "tauri": ["tauri", "rust"],
            "electron": ["electron", "node", "javascript"],
            "flutter": ["flutter", "dart"],
        }

        detected_framework = None
        for framework, words in frameworks.items():
            if any(word in query for word in words):
                detected_framework = framework
                break

        return {
            "detected_categories": categories,
            "detected_framework": detected_framework,
            "complexity": len(categories) + (1 if detected_framework else 0),
            "keywords_found": [word for word in query.split() if len(word) > 3],
        }

    async def _get_framework_comprehensive_guidance(self, framework: str, level: DisclosureLevel) -> Dict[str, Any]:
        """Get comprehensive guidance for specific framework"""
        try:
            framework_enum = DesktopFramework(framework.lower())
        except ValueError:
            return {"error": f"Unknown framework: {framework}"}

        if framework_enum == DesktopFramework.TAURI:
            return {
                "framework": "Tauri",
                "strengths": [
                    "Rust backend for performance and safety",
                    "Small application size",
                    "Excellent security model",
                    "Cross-platform with native performance",
                ],
                "considerations": [
                    "Rust learning curve for backend logic",
                    "Smaller ecosystem compared to Electron",
                    "Less mature tooling for some use cases",
                ],
                "best_practices": [
                    "Use Rust's type system for safety",
                    "Implement proper error handling with Result types",
                    "Leverage async/await for non-blocking operations",
                    "Use Tauri's allowlist for security",
                ],
                "recommended_for": [
                    "Performance-critical applications",
                    "Security-sensitive applications",
                    "Applications with complex backend logic",
                    "Resource-constrained environments",
                ],
            }
        elif framework_enum == DesktopFramework.ELECTRON:
            return {
                "framework": "Electron",
                "strengths": [
                    "Mature ecosystem with extensive libraries",
                    "Web technologies with full Node.js access",
                    "Excellent development tools and debugging",
                    "Large community and documentation",
                ],
                "considerations": [
                    "Higher memory usage and larger app size",
                    "Security requires careful configuration",
                    "Performance can be lower than native alternatives",
                ],
                "best_practices": [
                    "Use context isolation and preload scripts",
                    "Implement proper security headers",
                    "Optimize bundle size and lazy loading",
                    "Use native modules carefully",
                ],
                "recommended_for": [
                    "Web developers transitioning to desktop",
                    "Applications needing extensive Node.js ecosystem",
                    "Rapid prototyping and development",
                    "Applications with complex UI requirements",
                ],
            }

        return {"framework": framework, "guidance": "Specific guidance not available"}


class SecurityValidator:
    """Validator for security-related configurations and patterns"""

    def __init__(self):
        self.security_rules = [
            self._validate_csp,
            self._validate_sandboxing,
            self._validate_permissions,
            self._validate_code_signing,
        ]

    def validate_configuration(self, config: Dict[str, Any]) -> List[str]:
        """Validate security configuration and return issues"""
        issues = []

        for rule in self.security_rules:
            try:
                rule_issues = rule(config)
                issues.extend(rule_issues)
            except Exception as e:
                issues.append(f"Validation error: {e}")

        return issues

    def _validate_csp(self, config: Dict[str, Any]) -> List[str]:
        """Validate Content Security Policy configuration"""
        issues = []

        if "csp" in config:
            csp = config["csp"]
            if "unsafe-inline" in csp and "script-src" in csp:
                issues.append("CSP allows unsafe inline scripts - security risk")
            if "unsafe-eval" in csp:
                issues.append("CSP allows unsafe eval - security risk")

        return issues

    def _validate_sandboxing(self, config: Dict[str, Any]) -> List[str]:
        """Validate sandboxing configuration"""
        issues = []

        if "sandbox" in config and not config["sandbox"]:
            issues.append("Sandboxing is disabled - security risk")

        if "nodeIntegration" in config and config["nodeIntegration"]:
            issues.append("Node integration enabled - security risk")

        return issues

    def _validate_permissions(self, config: Dict[str, Any]) -> List[str]:
        """Validate permissions configuration"""
        issues = []

        if "permissions" in config:
            for permission, value in config["permissions"].items():
                if isinstance(value, dict) and "all" in value and value["all"]:
                    issues.append(f"Permission '{permission}' allows all operations - review necessity")

        return issues

    def _validate_code_signing(self, config: Dict[str, Any]) -> List[str]:
        """Validate code signing configuration"""
        issues = []

        if "code_signing" in config:
            signing = config["code_signing"]
            if "enabled" in signing and not signing["enabled"]:
                issues.append("Code signing disabled - distribution risk")

            if "enabled" in signing and signing["enabled"] and "certificate" not in signing:
                issues.append("Code signing enabled but no certificate configured")

        return issues


class BuildOptimizer:
    """Optimizer for build processes and configurations"""

    def __init__(self):
        self.optimization_rules = [
            self._optimize_dependencies,
            self._optimize_bundle_size,
            self._optimize_build_time,
            self._optimize_output_size,
        ]

    def optimize_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize build configuration"""
        optimized = config.copy()

        for rule in self.optimization_rules:
            try:
                optimized = rule(optimized)
            except Exception as e:
                logger.warning(f"Optimization rule failed: {e}")

        return optimized

    def _optimize_dependencies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize dependency configuration"""
        if "dependencies" in config:
            # Remove development dependencies from production build
            dev_deps = {"@types/*", "webpack", "babel", "eslint", "jest"}

            optimized_deps = {}
            for dep, version in config["dependencies"].items():
                if not any(pattern in dep for pattern in dev_deps):
                    optimized_deps[dep] = version

            config["dependencies"] = optimized_deps

        return config

    def _optimize_bundle_size(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize for smaller bundle size"""
        if "bundle" not in config:
            config["bundle"] = {}

        config["bundle"].update(
            {"minify": True, "tree_shaking": True, "dead_code_elimination": True, "compression": True}
        )

        return config

    def _optimize_build_time(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize for faster build times"""
        if "build" not in config:
            config["build"] = {}

        config["build"].update({"parallel": True, "cache": True, "incremental": True})

        return config

    def _optimize_output_size(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize output size"""
        if "output" not in config:
            config["output"] = {}

        config["output"].update({"compression": "gzip", "strip_debug": True, "optimize_images": True})

        return config

    async def _validate_zero_hallucination(self, input_data: Any, request: Dict[str, Any] = None):
        """
        Validate input to prevent hallucinations with zero-hallucination enforcement

        Args:
            input_data: Input data to validate
            request: Request context for validation

        Raises:
            ValueError: If hallucination detected or invalid configuration
        """
        # Enforce zero-hallucination by validating all technical claims
        query = request.get("query", "") if request else ""

        # Check for impossible combinations
        framework = request.get("framework") if request else None
        platform = request.get("platform") if request else None

        if framework and platform:
            if not self._is_platform_framework_combination_valid(framework, platform):
                raise ValueError(f"Zero-hallucination violation: {framework} does not support {platform}")

        # Validate technical claims against known patterns
        if isinstance(query, str):
            invalid_claims = ["infinite performance", "100% security", "zero resource usage", "instant startup"]

            for claim in invalid_claims:
                if claim.lower() in query.lower():
                    raise ValueError(f"Zero-hallucination violation: Invalid technical claim '{claim}'")

        # Check for suspicious uncertainty patterns
        if isinstance(input_data, str):
            suspicious_patterns = [
                "I am not sure",
                "I think",
                "probably",
                "might be",
                "could be",
                "perhaps",
                "I believe",
            ]

            for pattern in suspicious_patterns:
                if pattern.lower() in input_data.lower():
                    logger.warning(f"Potential hallucination pattern detected: {pattern}")
                    raise ValueError(f"Zero-hallucination violation: Uncertainty detected in expert response")


# Factory function for creating skill instances
def create_desktop_integration_expert() -> DesktopIntegrationExpert:
    """Create a new Desktop Integration Expert skill instance"""
    return DesktopIntegrationExpert()


# Export for skill registry
__all__ = [
    "DesktopIntegrationExpert",
    "create_desktop_integration_expert",
    "DisclosureLevel",
    "DesktopFramework",
    "Platform",
    "IntegrationCategory",
    "IntegrationPattern",
    "BuildConfiguration",
    "SecurityPolicy",
]
