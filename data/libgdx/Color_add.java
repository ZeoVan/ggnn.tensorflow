/**
 * Adds the given color component values to this Color's values.
 *
 * @param r Red component
 * @param g Green component
 * @param b Blue component
 * @param a Alpha component
 *
 * @return this Color for chaining
 */
public Color add(float r, float g, float b, float a) {
    this.r += r;
    this.g += g;
    this.b += b;
    this.a += a;
    return clamp();
}
