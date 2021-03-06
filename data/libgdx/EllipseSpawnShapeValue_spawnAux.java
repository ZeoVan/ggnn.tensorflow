@Override
public void spawnAux(Vector3 vector, float percent) {
    // Generate the point on the surface of the sphere
    float width = spawnWidth + spawnWidthDiff * spawnWidthValue.getScale(percent);
    float height = spawnHeight + spawnHeightDiff * spawnHeightValue.getScale(percent);
    float depth = spawnDepth + spawnDepthDiff * spawnDepthValue.getScale(percent);
    float radiusX, radiusY, radiusZ;
    // Where generate the point, on edges or inside ?
    float minT = 0, maxT = MathUtils.PI2;
    if (side == SpawnSide.top) {
        maxT = MathUtils.PI;
    } else if (side == SpawnSide.bottom) {
        maxT = -MathUtils.PI;
    }
    float t = MathUtils.random(minT, maxT);
    // Where generate the point, on edges or inside ?
    if (edges) {
        if (width == 0) {
            vector.set(0, height / 2 * MathUtils.sin(t), depth / 2 * MathUtils.cos(t));
            return;
        }
        if (height == 0) {
            vector.set(width / 2 * MathUtils.cos(t), 0, depth / 2 * MathUtils.sin(t));
            return;
        }
        if (depth == 0) {
            vector.set(width / 2 * MathUtils.cos(t), height / 2 * MathUtils.sin(t), 0);
            return;
        }
        radiusX = width / 2;
        radiusY = height / 2;
        radiusZ = depth / 2;
    } else {
        radiusX = MathUtils.random(width / 2);
        radiusY = MathUtils.random(height / 2);
        radiusZ = MathUtils.random(depth / 2);
    }
    float z = MathUtils.random(-1, 1f);
    float r = (float) Math.sqrt(1f - z * z);
    vector.set(radiusX * r * MathUtils.cos(t), radiusY * r * MathUtils.sin(t), radiusZ * z);
}
