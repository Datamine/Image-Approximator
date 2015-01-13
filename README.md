## Image-Approximator

Renders an image by splitting triangles, which yields a cool animation.

Requires: 
*PyGame 1.9.2a0
*Python Imaging Library 1.1.6+

## Todo

The following are areas for improvement:

* ~~There are currently lines drawn on the image as an artifact of the triangle-splitting. Should get rid of those lines -- they're ugly/distracting.~~
(Done, with an option to have them in the image for a more `tiled' look.)

* ~~Current rendering process is DFS. Should also have a BFS option.~~
(Done)

* Should split triangles into triangles of random dimensons, rather than into right-angle triangles (a bit boring).

* Could do this with random polygons at random positions. Maybe doing nothing but color inversions to approximate the image.

* This needs to be speeded up! Some optimization is called for.

* Should make a shortcut-mode that bypasses the animation and instead just renders the final image, directly.

* Does not yet work on certain grayscale images (e.g. Kitten.jpg.).
