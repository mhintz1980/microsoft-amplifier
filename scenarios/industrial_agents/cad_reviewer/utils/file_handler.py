"""
File handling utilities for CAD files.
"""

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Handler for loading and processing CAD files."""

    def __init__(self):
        self.supported_formats = {".step", ".stp", ".iges", ".igs", ".png", ".jpg", ".jpeg", ".svg"}

    async def load_cad_file(self, file_path: Path) -> dict[str, Any]:
        """Load CAD file and extract data for analysis."""
        logger.info(f"Loading CAD file: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"CAD file not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix in {".step", ".stp"}:
            return await self._load_step_file(file_path)
        elif suffix in {".iges", ".igs"}:
            return await self._load_iges_file(file_path)
        elif suffix in {".png", ".jpg", ".jpeg"}:
            return await self._load_image_file(file_path)
        elif suffix == ".svg":
            return await self._load_svg_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    async def detect_software(self, file_path: Path) -> str | None:
        """Detect the CAD software that created the file."""
        suffix = file_path.suffix.lower()

        if suffix in {".step", ".stp"}:
            return await self._detect_step_software(file_path)
        elif suffix in {".iges", ".igs"}:
            return await self._detect_iges_software(file_path)
        else:
            return None

    async def detect_units(self, file_path: Path) -> str | None:
        """Detect units used in the CAD file."""
        # This is a simplified implementation
        # In practice, you'd parse the file headers to detect units
        return "mm"  # Default assumption

    async def extract_bounding_box(self, file_path: Path) -> dict[str, float] | None:
        """Extract 3D bounding box from CAD file."""
        # This is a simplified implementation
        # In practice, you'd parse the geometry to calculate actual bounds
        return {"min_x": 0.0, "max_x": 100.0, "min_y": 0.0, "max_y": 100.0, "min_z": 0.0, "max_z": 50.0}

    async def _load_step_file(self, file_path: Path) -> dict[str, Any]:
        """Load STEP file data."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse STEP file header for metadata
            header_info = self._parse_step_header(content)

            # Extract geometric data (simplified)
            geometry_data = await self._extract_step_geometry(content)

            return {
                "file_type": "STEP",
                "content": content[:10000],  # Truncate for memory
                "header": header_info,
                "geometry": geometry_data,
                "image_data": await self._generate_preview_image(geometry_data),
            }

        except Exception as e:
            logger.error(f"Error loading STEP file {file_path}: {e}")
            raise

    async def _load_iges_file(self, file_path: Path) -> dict[str, Any]:
        """Load IGES file data."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse IGES file header
            header_info = self._parse_iges_header(content)

            # Extract geometric data (simplified)
            geometry_data = await self._extract_iges_geometry(content)

            return {
                "file_type": "IGES",
                "content": content[:10000],
                "header": header_info,
                "geometry": geometry_data,
                "image_data": await self._generate_preview_image(geometry_data),
            }

        except Exception as e:
            logger.error(f"Error loading IGES file {file_path}: {e}")
            raise

    async def _load_image_file(self, file_path: Path) -> dict[str, Any]:
        """Load image file data."""
        try:
            # Load image with OpenCV
            image = cv2.imread(str(file_path))
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")

            # Extract basic image features
            features = await self._extract_image_features(image)

            return {
                "file_type": "IMAGE",
                "image_data": image,
                "features": features,
                "geometry": await self._infer_geometry_from_image(image),
            }

        except Exception as e:
            logger.error(f"Error loading image file {file_path}: {e}")
            raise

    async def _load_svg_file(self, file_path: Path) -> dict[str, Any]:
        """Load SVG file data."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse SVG content (simplified)
            svg_data = self._parse_svg_content(content)

            return {
                "file_type": "SVG",
                "content": content,
                "svg_data": svg_data,
                "geometry": await self._extract_svg_geometry(svg_data),
            }

        except Exception as e:
            logger.error(f"Error loading SVG file {file_path}: {e}")
            raise

    def _parse_step_header(self, content: str) -> dict[str, Any]:
        """Parse STEP file header information."""
        header_info = {}

        # Look for common STEP header fields
        lines = content.split("\n")
        for line in lines:
            if "FILE_DESCRIPTION" in line:
                header_info["description"] = line.strip()
            elif "FILE_NAME" in line:
                header_info["file_name"] = line.strip()
            elif "FILE_SCHEMA" in line:
                header_info["schema"] = line.strip()

        return header_info

    def _parse_iges_header(self, content: str) -> dict[str, Any]:
        """Parse IGES file header information."""
        header_info = {}

        # Look for IGES header section (starts with S)
        lines = content.split("\n")
        for line in lines:
            if line.startswith("S") and len(line) > 72:
                header_data = line[72:].strip()
                if header_data:
                    header_info["header_info"] = header_data

        return header_info

    def _parse_svg_content(self, content: str) -> dict[str, Any]:
        """Parse SVG content for geometric information."""
        # Simplified SVG parsing
        svg_data = {"elements": [], "viewBox": None, "dimensions": None}

        # Extract viewBox
        if "viewBox=" in content:
            import re

            viewBox_match = re.search(r'viewBox="([^"]+)"', content)
            if viewBox_match:
                svg_data["viewBox"] = viewBox_match.group(1)

        return svg_data

    async def _extract_step_geometry(self, content: str) -> dict[str, Any]:
        """Extract geometric data from STEP file."""
        # Simplified geometry extraction
        geometry = {"entities": [], "surface_area": 0.0, "volume": 0.0, "surface_area_to_volume_ratio": 0.0}

        # Count geometric entities (simplified)
        entity_count = content.count("ADVANCED_BREP_SHAPE_REPRESENTATION")
        geometry["entities"] = [{"type": "brep", "id": i} for i in range(entity_count)]

        # Mock geometric calculations
        geometry["surface_area"] = 10000.0 + entity_count * 100
        geometry["volume"] = 5000.0 + entity_count * 50

        if geometry["volume"] > 0:
            geometry["surface_area_to_volume_ratio"] = geometry["surface_area"] / geometry["volume"]

        return geometry

    async def _extract_iges_geometry(self, content: str) -> dict[str, Any]:
        """Extract geometric data from IGES file."""
        # Simplified geometry extraction
        geometry = {"entities": [], "surface_area": 0.0, "volume": 0.0, "surface_area_to_volume_ratio": 0.0}

        # Count geometric entities (simplified)
        # Look for common IGES entity types
        entity_types = ["128", "144", "186"]  # Surface entities
        total_entities = sum(content.count(f"  {etype}") for etype in entity_types)

        geometry["entities"] = [{"type": "surface", "id": i} for i in range(total_entities)]

        # Mock geometric calculations
        geometry["surface_area"] = 8000.0 + total_entities * 80
        geometry["volume"] = 4000.0 + total_entities * 40

        if geometry["volume"] > 0:
            geometry["surface_area_to_volume_ratio"] = geometry["surface_area"] / geometry["volume"]

        return geometry

    async def _extract_image_features(self, image: np.ndarray) -> dict[str, Any]:
        """Extract features from image for analysis."""
        features = {
            "dimensions": image.shape[:2],
            "mean_intensity": np.mean(image),
            "std_intensity": np.std(image),
            "edge_density": 0.0,
        }

        # Calculate edge density
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150)
        features["edge_density"] = np.sum(edges > 0) / edges.size

        return features

    async def _infer_geometry_from_image(self, image: np.ndarray) -> dict[str, Any]:
        """Infer geometric properties from image."""
        # Simplified geometric inference
        geometry = {"surface_area": 0.0, "volume": 0.0, "aspect_ratios": [1.0], "complexity_score": 0.0}

        # Calculate complexity based on edge density
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150)
        geometry["complexity_score"] = np.sum(edges > 0) / edges.size

        # Mock aspect ratio based on image dimensions
        h, w = image.shape[:2]
        geometry["aspect_ratios"] = [w / h if h > 0 else 1.0]

        return geometry

    async def _extract_svg_geometry(self, svg_data: dict[str, Any]) -> dict[str, Any]:
        """Extract geometric data from SVG."""
        geometry = {
            "surface_area": 0.0,
            "volume": 0.0,
            "elements_count": len(svg_data.get("elements", [])),
            "viewBox": svg_data.get("viewBox"),
        }

        return geometry

    async def _generate_preview_image(self, geometry_data: dict[str, Any]) -> np.ndarray | None:
        """Generate a preview image from geometric data."""
        # Create a simple placeholder image
        # In practice, you'd render the actual geometry
        preview = np.zeros((400, 400, 3), dtype=np.uint8)
        preview[:] = (50, 50, 50)  # Gray background

        # Add some simple geometric shapes to represent the CAD model
        cv2.rectangle(preview, (100, 100), (300, 300), (100, 150, 200), 2)
        cv2.circle(preview, (200, 200), 50, (150, 100, 200), 2)

        return preview

    async def _detect_step_software(self, file_path: Path) -> str | None:
        """Detect software from STEP file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read(2000)  # Read first 2KB

            # Look for software signatures
            if "SolidWorks" in content:
                return "SolidWorks"
            elif "Autodesk" in content:
                return "Autodesk"
            elif "Siemens" in content:
                return "Siemens NX"
            elif "Dassault" in content:
                return "CATIA"
            else:
                return "Unknown"

        except Exception:
            return None

    async def _detect_iges_software(self, file_path: Path) -> str | None:
        """Detect software from IGES file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read(2000)  # Read first 2KB

            # Look for software signatures in IGES header
            if "SolidWorks" in content:
                return "SolidWorks"
            elif "Autodesk" in content:
                return "Autodesk"
            elif "Pro/E" in content or "Creo" in content:
                return "PTC Creo"
            else:
                return "Unknown"

        except Exception:
            return None
