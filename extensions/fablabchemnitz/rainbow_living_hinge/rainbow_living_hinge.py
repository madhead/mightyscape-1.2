#!/usr/bin/env python3
"""
rainbow_living_hinge.py
A module for creating lines for laser cut coffee cup holders.

Copyright (C) 2023 madhead; siarhei.krukau@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For a copy of the GNU General Public License
write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

"""
Change in version 0.1.
Initial implementation.
"""
__version__ = "0.1"

import inkex

from lxml import etree

class RainbowLivingHinge(inkex.EffectExtension):
  def add_arguments(self, pars):
      pars.add_argument('--angle', type=float, default=40, help='Apex Angle (degrees)')
      pars.add_argument('--arc', type=float, default=230, help='Arc (mm)')
      pars.add_argument('--height', type=float, default=60, help='Height (mm)')
      pars.add_argument('--horizontalLineSeparation', type=float, default=1, help='Horizontal Line Separation (mm)')
      pars.add_argument('--verticalLineSeparation', type=float, default=3, help='Vertical Line Separation (mm)')
      pars.add_argument('--maxLineLength', type=float, default=30, help='Max Line Length (mm)')
      pars.add_argument('--constructionGeometry', type=inkex.Boolean, default=False, help='Draw Construction Geometry')

  def effect(self):
    layer = self.svg.get_current_layer()

    if self.options.constructionGeometry is True:
       self.drawConstructionGeometry(layer)

  def drawConstructionGeometry(self, layer):
    geometry = etree.SubElement(layer, 'g')
    ## Define the center of the image
    center_x = self.svg.viewport_width / 2
    center_y = self.svg.viewport_height / 2

    center = etree.SubElement(geometry, inkex.addNS('circle','svg'))
    center.set('style', 'fill:#000000;fill-opacity:1')
    center.set('cx', str(center_x))
    center.set('cy', str(center_y))
    center.set('r', '10')


if __name__ == '__main__':
    RainbowLivingHinge().run()
