/**
 * Postmultiplies this matrix with a (counter-clockwise) rotation matrix.
 * @param radians The angle in radians
 * @return This matrix for the purpose of chaining.
 */
public Affine2 rotateRad(float radians) {
    if (radians == 0)
        return this;
    float cos = MathUtils.cos(radians);
    float sin = MathUtils.sin(radians);
    float tmp00 = m00 * cos + m01 * sin;
    float tmp01 = m00 * -sin + m01 * cos;
    float tmp10 = m10 * cos + m11 * sin;
    float tmp11 = m10 * -sin + m11 * cos;
    m00 = tmp00;
    m01 = tmp01;
    m10 = tmp10;
    m11 = tmp11;
    return this;
}
