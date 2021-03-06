private final static void transformNormal(final float[] values, final int offset, final int size, Matrix3 transform) {
    if (size > 2) {
        vTmp.set(values[offset], values[offset + 1], values[offset + 2]).mul(transform).nor();
        values[offset] = vTmp.x;
        values[offset + 1] = vTmp.y;
        values[offset + 2] = vTmp.z;
    } else if (size > 1) {
        vTmp.set(values[offset], values[offset + 1], 0).mul(transform).nor();
        values[offset] = vTmp.x;
        values[offset + 1] = vTmp.y;
    } else
        values[offset] = vTmp.set(values[offset], 0, 0).mul(transform).nor().x;
}
