/**
 * Draws a circle outline with the center at x,y and a radius using the current color and stroke width.
 *
 * @param x The x-coordinate of the center
 * @param y The y-coordinate of the center
 * @param radius The radius in pixels
 */
public void drawCircle(int x, int y, int radius) {
    circle(x, y, radius, DrawType.STROKE);
}