#!/usr/bin/env python3

import math
import inkex
from inkex.transforms import Transform

class IsometricProjection(inkex.EffectExtension):
    """
    Convert a flat 2D projection to one of the three visible sides in an
    isometric projection, and vice versa.
    """

    attrTransformCenterX = inkex.addNS('transform-center-x', 'inkscape')
    attrTransformCenterY = inkex.addNS('transform-center-y', 'inkscape')

    # Precomputed values for sine, cosine, and tangent of 30°.
    rad_30 = math.radians(30)
    cos_30 = math.cos(rad_30)
    sin_30 = 0.5  # No point in using math.sin for 30°.
    tan_30 = math.tan(rad_30)

    # Combined affine transformation matrices. The bottom row of these 3×3
    # matrices is omitted; it is always [0, 0, 1].
    transformations = {
        # From 2D to isometric top down view:
        #   * scale vertically by cos(30°)
        #   * shear horizontally by -30°
        #   * rotate clock-wise 30°
        'to_top':       [[cos_30,       -cos_30,    0],
                         [sin_30,       sin_30,     0]],

        # From 2D to isometric left-hand side view:
        #   * scale horizontally by cos(30°)
        #   * shear vertically by -30°
        'to_left':      [[cos_30,       0,          0],
                         [sin_30,       1,          0]],

        # From 2D to isometric right-hand side view:
        #   * scale horizontally by cos(30°)
        #   * shear vertically by 30°
        'to_right':     [[cos_30,       0,          0],
                         [-sin_30,      1,          0]],

        # From isometric top down view to 2D:
        #   * rotate counter-clock-wise 30°
        #   * shear horizontally by 30°
        #   * scale vertically by 1 / cos(30°)
        'from_top':     [[tan_30,       1,          0],
                         [-tan_30,      1,          0]],

        # From isometric left-hand side view to 2D:
        #   * shear vertically by 30°
        #   * scale horizontally by 1 / cos(30°)
        'from_left':    [[1 / cos_30,   0,          0],
                         [-tan_30,      1,          0]],

        # From isometric right-hand side view to 2D:
        #   * shear vertically by -30°
        #   * scale horizontally by 1 / cos(30°)
        'from_right':   [[1 / cos_30,   0,          0],
                         [tan_30,       1,          0]]
    }

    def add_arguments(self, pars):
        pars.add_argument('--conversion', default='top', help='Conversion to perform: (top|left|right)')
        pars.add_argument('--reverse', type=inkex.Boolean, default=False, help='Reverse the transformation from isometric projection to flat 2D')
        self.arg_parser.add_argument('--orthoangle', type=float, default=15.0, help='Isometric angle in degrees')

    def __initConstants(self, angle):
        # Precomputed values for sine, cosine, and tangent of orthoangle.
        self.rad = math.radians(angle)
        self.cos = math.cos(self.rad)
        self.sin = math.sin(self.rad)
        self.tan = math.tan(self.rad)

        # Combined affine transformation matrices. The bottom row of these 3×3
        # matrices is omitted; it is always [0, 0, 1].
        self.transformations = {
            # From 2D to isometric top down view:
            #   * scale vertically by cos(∠)
            #   * shear horizontally by -∠
            #   * rotate clock-wise ∠
            'to_top':       Transform(((self.cos,         -self.cos,        0),
                                       (self.sin,         self.sin,         0))),

            # From 2D to isometric left-hand side view:
            #   * scale horizontally by cos(∠)
            #   * shear vertically by -∠
            'to_left':      Transform(((self.cos,         0,                0),
                                       (self.sin,         1,                0))),

            # From 2D to isometric right-hand side view:
            #   * scale horizontally by cos(∠)
            #   * shear vertically by ∠
            'to_right':     Transform(((self.cos ,        0,                0),
                                       (-self.sin,        1,                0))),

            # From isometric top down view to 2D:
            #   * rotate counter-clock-wise orthoangle
            #   * shear horizontally by orthoangle
            #   * scale vertically by 1 / cos(orthoangle)
            'from_top':     [[self.tan ,      1,          0],
                             [-self.tan,      1,          0]],
 
            # From isometric left-hand side view to 2D:
            #   * shear vertically by orthoangle
            #   * scale horizontally by 1 / cos(orthoangle)
            'from_left':    [[1 / self.cos,   0,          0],
                             [-self.tan,      1,          0]],

            # From isometric right-hand side view to 2D:
            #   * shear vertically by -orthoangle
            #   * scale horizontally by 1 / cos(orthoangle)
            'from_right':   [[1 / self.cos,   0,          0],
                             [self.tan,       1,          0]]
        }

        # The inverse matrices of the above perform the reverse transformations.
        self.transformations['from_top'] = -self.transformations['to_top']
        self.transformations['from_left'] = -self.transformations['to_left']
        self.transformations['from_right'] = -self.transformations['to_right']

    def getTransformCenter(self, midpoint, node):
        """
        Find the transformation center of an object. If the user set it
        manually by dragging it in Inkscape, those coordinates are used.
        Otherwise, an attempt is made to find the center of the object's
        bounding box.
        """

        c_x = node.get(self.attrTransformCenterX)
        c_y = node.get(self.attrTransformCenterY)

        # Default to dead-center.
        if c_x is None:
            c_x = 0.0
        else:
            c_x = float(c_x)
        if c_y is None:
            c_y = 0.0
        else:
            c_y = float(c_y)

        x = midpoint[0] + c_x
        y = midpoint[1] - c_y

        return [x, y]

    def translateBetweenPoints(self, tr, here, there):
        """
        Add a translation to a matrix that moves between two points.
        """

        x = there[0] - here[0]
        y = there[1] - here[1]
        tr.add_translate(x, y)

    def moveTransformationCenter(self, node, midpoint, center_new):
        """
        If a transformation center is manually set on the node, move it to
        match the transformation performed on the node.
        """

        c_x = node.get(self.attrTransformCenterX)
        c_y = node.get(self.attrTransformCenterY)

        if c_x is not None:
            x = str(center_new[0] - midpoint[0])
            node.set(self.attrTransformCenterX, x)
        if c_y is not None:
            y = str(midpoint[1] - center_new[1])
            node.set(self.attrTransformCenterY, y)

    def effect(self):
        
        self.__initConstants(self.options.orthoangle)
        
        if self.options.reverse is True:
            conversion = "from_" + self.options.conversion
        else:
            conversion = "to_" + self.options.conversion

        if len(self.svg.selected) == 0:
            inkex.errormsg("Please select an object to perform the " +
                             "isometric projection transformation on.")
            return

        # Default to the flat 2D to isometric top down view conversion if an
        # invalid identifier is passed.
        effect_matrix = self.transformations.get(
            conversion, self.transformations.get('to_top'))

        for id, node in self.svg.selected.items():
            bbox = node.bounding_box()
            midpoint = [bbox.center_x, bbox.center_y]
            center_old = self.getTransformCenter(midpoint, node)
            transform = Transform(node.get("transform"))
            # Combine our transformation matrix with any pre-existing transform.
            tr = transform @ effect_matrix

            # Compute the location of the transformation center after applying
            # the transformation matrix.
            center_new = center_old[:]
            #Transform(matrix).apply_to_point(center_new)
            tr.apply_to_point(center_new)
            tr.apply_to_point(midpoint)

            # Add a translation transformation that will move the object to
            # keep its transformation center in the same place.
            self.translateBetweenPoints(tr, center_new, center_old)

            node.set('transform', str(tr))

            # Adjust the transformation center.
            self.moveTransformationCenter(node, midpoint, center_new)

if __name__ == '__main__':
    IsometricProjection().run()