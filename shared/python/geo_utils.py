"""
Shared geographic utility functions for GPX/GeoJSON processing.

This module provides common functions used across the phillongworth-site
build scripts for calculating distances and simplifying polylines.
"""

import math


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Args:
        lat1, lon1: Latitude and longitude of first point (degrees)
        lat2, lon2: Latitude and longitude of second point (degrees)

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def perpendicular_distance(point: tuple, line_start: tuple, line_end: tuple) -> float:
    """
    Calculate the perpendicular distance from a point to a line segment.

    Args:
        point: (x, y) tuple for the point
        line_start: (x, y) tuple for line segment start
        line_end: (x, y) tuple for line segment end

    Returns:
        Distance in the same units as the input coordinates
    """
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]
    if dx == 0 and dy == 0:
        return math.hypot(point[0] - line_start[0], point[1] - line_start[1])
    t = ((point[0] - line_start[0]) * dx + (point[1] - line_start[1]) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    proj_x = line_start[0] + t * dx
    proj_y = line_start[1] + t * dy
    return math.hypot(point[0] - proj_x, point[1] - proj_y)


def douglas_peucker(points: list, tolerance: float) -> list:
    """
    Simplify a polyline using the Douglas-Peucker algorithm.

    This algorithm recursively removes points that deviate less than
    the tolerance from the line between their neighbors.

    Args:
        points: List of (x, y) tuples representing the polyline
        tolerance: Maximum allowed deviation (in same units as coordinates)

    Returns:
        Simplified list of (x, y) tuples
    """
    if len(points) <= 2:
        return points

    max_dist = 0
    max_idx = 0
    for i in range(1, len(points) - 1):
        d = perpendicular_distance(points[i], points[0], points[-1])
        if d > max_dist:
            max_dist = d
            max_idx = i

    if max_dist > tolerance:
        left = douglas_peucker(points[:max_idx + 1], tolerance)
        right = douglas_peucker(points[max_idx:], tolerance)
        return left[:-1] + right
    else:
        return [points[0], points[-1]]


# Unit conversion constants
KM_TO_MILES = 0.621371
METERS_TO_FEET = 3.28084
