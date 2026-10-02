from svgpathtools import svg2paths

from PIL import Image
from PIL import ImageDraw

import numpy as np

from skimage.morphology import skeletonize


def svg_to_skeleton(
    svg_file,
    samples=12000
):

    paths, _ = svg2paths(
        str(svg_file)
    )

    path = paths[0]

    polygon = []

    for i in range(samples):

        p = path.point(
            i/(samples-1)
        )

        polygon.append(
            (
                float(p.real),
                float(p.imag)
            )
        )

    img = Image.new(
        "L",
        (1920,1080),
        0
    )

    draw = ImageDraw.Draw(
        img
    )

    draw.polygon(
        polygon,
        fill=255
    )

    binary = (
        np.array(img)
        > 0
    )

    return skeletonize(
        binary
    )
