@Override
public void glUniform4fv(int location, int count, float[] v, int offset) {
    calls++;
    gl30.glUniform4fv(location, count, v, offset);
    check();
}
