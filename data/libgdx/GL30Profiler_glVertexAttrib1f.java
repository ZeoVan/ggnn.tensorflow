@Override
public void glVertexAttrib1f(int indx, float x) {
    calls++;
    gl30.glVertexAttrib1f(indx, x);
    check();
}
