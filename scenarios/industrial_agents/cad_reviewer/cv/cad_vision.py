"""
Computer vision tools for CAD image analysis.
"""

from typing import Any

import cv2
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CADVisionAnalyzer:
    """Computer vision analyzer for CAD files and images."""

    def __init__(self):
        self.edge_detection_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])

    async def analyze_acoustic_features(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze CAD data for acoustic-related features."""
        logger.info("Analyzing acoustic features with computer vision...")

        results = {"weak_points": [], "openings": [], "thin_sections": [], "material_transitions": []}

        try:
            # Extract geometric features from CAD data
            if "image_data" in cad_data:
                image = cad_data["image_data"]

                # Detect openings and gaps (acoustic weak points)
                openings = await self._detect_openings(image)
                results["openings"] = openings

                # Detect thin sections (poor acoustic insulation)
                thin_sections = await self._detect_thin_sections(image)
                results["thin_sections"] = thin_sections

                # Detect material transitions
                material_transitions = await self._detect_material_transitions(image)
                results["material_transitions"] = material_transitions

            # Analyze 3D geometry if available
            if "geometry" in cad_data:
                geometry_analysis = await self._analyze_3d_geometry_acoustic(cad_data["geometry"])
                results.update(geometry_analysis)

            # Generate weak points list
            results["weak_points"] = await self._identify_acoustic_weak_points(results)

        except Exception as e:
            logger.error(f"Error in acoustic feature analysis: {e}")
            results["error"] = str(e)

        return results

    async def analyze_structural_features(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze CAD data for structural features."""
        logger.info("Analyzing structural features with computer vision...")

        results = {"stress_concentrations": [], "load_paths": [], "connections": [], "supports": []}

        try:
            if "image_data" in cad_data:
                image = cad_data["image_data"]

                # Detect stress concentration points
                stress_points = await self._detect_stress_concentrations(image)
                results["stress_concentrations"] = stress_points

                # Identify load paths
                load_paths = await self._identify_load_paths(image)
                results["load_paths"] = load_paths

                # Detect connections and joints
                connections = await self._detect_connections(image)
                results["connections"] = connections

            if "geometry" in cad_data:
                geometry_analysis = await self._analyze_3d_geometry_structural(cad_data["geometry"])
                results.update(geometry_analysis)

        except Exception as e:
            logger.error(f"Error in structural feature analysis: {e}")
            results["error"] = str(e)

        return results

    async def analyze_manufacturing_features(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze CAD data for manufacturing features."""
        logger.info("Analyzing manufacturing features with computer vision...")

        results = {
            "tool_access_issues": [],
            "complex_features": [],
            "tolerance_critical_areas": [],
            "machining_features": [],
        }

        try:
            if "image_data" in cad_data:
                image = cad_data["image_data"]

                # Detect tool access issues
                tool_access = await self._detect_tool_access_issues(image)
                results["tool_access_issues"] = tool_access

                # Identify complex features
                complex_features = await self._identify_complex_features(image)
                results["complex_features"] = complex_features

                # Detect tolerance critical areas
                tolerance_areas = await self._detect_tolerance_critical_areas(image)
                results["tolerance_critical_areas"] = tolerance_areas

            if "geometry" in cad_data:
                geometry_analysis = await self._analyze_3d_geometry_manufacturing(cad_data["geometry"])
                results.update(geometry_analysis)

        except Exception as e:
            logger.error(f"Error in manufacturing feature analysis: {e}")
            results["error"] = str(e)

        return results

    async def _detect_openings(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Detect openings and gaps in the CAD image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use adaptive thresholding to find openings
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        openings = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                openings.append(
                    {"location": (int(x + w / 2), int(y + h / 2)), "size": (w, h), "area": area, "type": "opening"}
                )

        return openings

    async def _detect_thin_sections(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Detect thin sections that may have poor acoustic properties."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use morphological operations to identify thin regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
        morph = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)

        # Threshold to find thin lines
        _, thin_mask = cv2.threshold(morph, 30, 255, cv2.THRESH_BINARY)

        # Find thin section contours
        contours, _ = cv2.findContours(thin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        thin_sections = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                x, y, w, h = cv2.boundingRect(contour)
                if min(w, h) < 5:  # Thin dimension threshold
                    thin_sections.append(
                        {
                            "location": (int(x + w / 2), int(y + h / 2)),
                            "dimensions": (w, h),
                            "thickness": min(w, h),
                            "type": "thin_section",
                        }
                    )

        return thin_sections

    async def _detect_material_transitions(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Detect material transitions that may affect acoustic performance."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use edge detection to find material boundaries
        edges = cv2.Canny(gray, 50, 150)

        # Use Hough lines to find straight edges (material boundaries)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

        transitions = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if length > 30:  # Filter short edges
                    transitions.append(
                        {
                            "start_point": (int(x1), int(y1)),
                            "end_point": (int(x2), int(y2)),
                            "length": length,
                            "type": "material_transition",
                        }
                    )

        return transitions

    async def _detect_stress_concentrations(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Detect potential stress concentration points."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use corner detection for stress concentration points
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10, blockSize=3)

        stress_points = []
        if corners is not None:
            for corner in corners:
                x, y = corner.ravel()
                stress_points.append(
                    {"location": (int(x), int(y)), "type": "corner", "stress_type": "potential_concentration"}
                )

        # Look for holes (common stress concentrators)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=5, maxRadius=50)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                center = (circle[0], circle[1])
                radius = circle[2]
                stress_points.append(
                    {"location": center, "radius": radius, "type": "hole", "stress_type": "stress_concentration"}
                )

        return stress_points

    async def _identify_load_paths(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Identify potential load paths in the structure."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use skeletonization to find structural paths
        binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
        skeleton = cv2.ximgproc.thinning(binary)

        # Find connected components (potential load paths)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skeleton)

        load_paths = []
        for i in range(1, num_labels):  # Skip background (0)
            if stats[i, cv2.CC_STAT_AREA] > 100:  # Filter small components
                load_paths.append(
                    {"centroid": centroids[i].tolist(), "area": stats[i, cv2.CC_STAT_AREA], "type": "load_path"}
                )

        return load_paths

    async def _detect_connections(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Detect connections and joints between components."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use template matching for common joint patterns
        # This is a simplified approach - in practice, you'd use more sophisticated methods

        # Look for intersection points
        intersections = cv2.cornerHarris(gray, 2, 3, 0.04)
        corners = np.where(intersections > 0.01 * intersections.max())

        connections = []
        for y, x in zip(corners[0], corners[1], strict=False):
            connections.append(
                {"location": (int(x), int(y)), "type": "joint", "confidence": float(intersections[y, x])}
            )

        return connections

    async def _detect_tool_access_issues(self, image: np.ndarray) -> list[str]:
        """Detect potential tool access issues for manufacturing."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        issues = []

        # Look for enclosed areas (hard to access)
        binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 500:
                # Check if contour is enclosed
                hull = cv2.convexHull(contour)
                if len(hull) > 10:  # Complex shape
                    issues.append("Complex enclosed feature may be difficult to machine")

        # Look for deep features
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=10)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if length > 200:
                    issues.append("Deep feature detected - may require specialized tooling")

        return list(set(issues))  # Remove duplicates

    async def _identify_complex_features(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Identify complex geometric features."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        features = []

        # Look for curves (complex compared to straight lines)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 100:
                # Approximate contour to check complexity
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                if len(approx) > 10:  # Complex shape
                    x, y, w, h = cv2.boundingRect(contour)
                    features.append(
                        {
                            "location": (int(x + w / 2), int(y + h / 2)),
                            "complexity": len(approx),
                            "type": "complex_feature",
                        }
                    )

        return features

    async def _detect_tolerance_critical_areas(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Detect areas that may require tight tolerances."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        critical_areas = []

        # Look for holes and features that typically need tight tolerances
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=3, maxRadius=30)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                center = (circle[0], circle[1])
                radius = circle[2]
                critical_areas.append({"location": center, "radius": radius, "type": "hole_tolerance_critical"})

        return critical_areas

    async def _analyze_3d_geometry_acoustic(self, geometry: dict[str, Any]) -> dict[str, Any]:
        """Analyze 3D geometry for acoustic properties."""
        results = {}

        if "mesh" in geometry:
            mesh = geometry["mesh"]
            # Analyze mesh for acoustic properties
            # This is a placeholder for actual 3D geometry analysis
            results["surface_area"] = mesh.get("surface_area", 0)
            results["volume"] = mesh.get("volume", 0)

        return results

    async def _analyze_3d_geometry_structural(self, geometry: dict[str, Any]) -> dict[str, Any]:
        """Analyze 3D geometry for structural properties."""
        results = {}

        if "mesh" in geometry:
            mesh = geometry["mesh"]
            # Analyze mesh for structural properties
            results["aspect_ratios"] = mesh.get("aspect_ratios", [])
            results["element_quality"] = mesh.get("element_quality", 0)

        return results

    async def _analyze_3d_geometry_manufacturing(self, geometry: dict[str, Any]) -> dict[str, Any]:
        """Analyze 3D geometry for manufacturing properties."""
        results = {}

        if "mesh" in geometry:
            mesh = geometry["mesh"]
            # Analyze mesh for manufacturing properties
            results["undercuts"] = mesh.get("undercuts", [])
            results["draft_angles"] = mesh.get("draft_angles", [])

        return results

    async def _identify_acoustic_weak_points(self, acoustic_results: dict[str, Any]) -> list[str]:
        """Identify and categorize acoustic weak points."""
        weak_points = []

        # Add openings as weak points
        for opening in acoustic_results.get("openings", []):
            weak_points.append(f"Opening detected at {opening['location']} with area {opening['area']:.1f} px²")

        # Add thin sections as weak points
        for thin_section in acoustic_results.get("thin_sections", []):
            weak_points.append(
                f"Thin section detected at {thin_section['location']} with thickness {thin_section['thickness']} px"
            )

        # Add material transitions
        for transition in acoustic_results.get("material_transitions", []):
            weak_points.append(
                f"Material transition detected from {transition['start_point']} to {transition['end_point']}"
            )

        return weak_points
