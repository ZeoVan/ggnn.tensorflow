/**
 * Invalidates the VertexBufferObject so a new OpenGL buffer handle is created. Use this in case of a context loss.
 */
@Override
public void invalidate() {
    bufferHandle = Gdx.gl20.glGenBuffer();
    isDirty = true;
    vaoDirty = true;
}
