/**
 * Sets the Color components using the specified integer value in the format RGBA8888. This is inverse to the rgba8888(r, g,
 * b, a) method.
 *
 * @param color The Color to be modified.
 * @param value An integer color value in RGBA8888 format.
 */
public static void rgba8888ToColor(Color color, int value) {
    color.r = ((value & 0xff000000) >>> 24) / 255f;
    color.g = ((value & 0x00ff0000) >>> 16) / 255f;
    color.b = ((value & 0x0000ff00) >>> 8) / 255f;
    color.a = ((value & 0x000000ff)) / 255f;
}
