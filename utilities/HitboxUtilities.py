import math

import pygame


def polygons_collide(poly1, poly2):
    """
    Check if two polygons collide using the Separating Axis Theorem (SAT).

    SAT states that two convex polygons do not overlap if there exists
    an axis along which the projections of the two polygons do not overlap.

    Args:
        poly1 (list of tuples): List of (x, y) tuples representing the vertices of the first polygon.
        poly2 (list of tuples): List of (x, y) tuples representing the vertices of the second polygon.

    Returns:
        bool: True if polygons collide (overlap), False otherwise.
    """
    def get_axes(poly):
        """
                Calculate the normals (axes) to each edge of the polygon.

                Args:
                    poly (list of tuples): Polygon vertices.

                Returns:
                    list of pygame.Vector2: Normalized perpendicular vectors (axes) to polygon edges.
                """
        axes = []
        for i in range(len(poly)):
            p1 = pygame.Vector2(poly[i])
            p2 = pygame.Vector2(poly[(i + 1) % len(poly)])
            edge = p2 - p1
            normal = pygame.Vector2(-edge.y, edge.x).normalize()
            axes.append(normal)
        return axes

    def project(poly, axis):
        """
        Project all polygon vertices onto an axis.

        Args:
            poly (list of tuples): Polygon vertices.
            axis (pygame.Vector2): Axis vector to project onto.

        Returns:
            tuple: (min_proj, max_proj) projection scalar values along the axis.
        """
        dots = [pygame.Vector2(p).dot(axis) for p in poly]
        return min(dots), max(dots)

    axes = get_axes(poly1) + get_axes(poly2)
    for axis in axes:
        min1, max1 = project(poly1, axis)
        min2, max2 = project(poly2, axis)
        if max1 < min2 or max2 < min1:
            return False  # No overlap on this axis
    return True

def rotate_point(point, angle, origin):
    """
    Rotate a point around a given origin by an angle in degrees.

    Args:
        point (tuple): (x, y) coordinates of the point to rotate.
        angle (float): Rotation angle in degrees.
        origin (tuple): (x, y) coordinates of the rotation origin.

    Returns:
        tuple: (x, y) coordinates of the rotated point.
    """
    angle_rad = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
    qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
    return (qx, qy)


def point_distance(p1, p2):
    """
    Calculate the Euclidean distance between two points.

    Args:
        p1 (tuple): (x, y) coordinates of the first point.
        p2 (tuple): (x, y) coordinates of the second point.

    Returns:
        float: Distance between the two points.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
