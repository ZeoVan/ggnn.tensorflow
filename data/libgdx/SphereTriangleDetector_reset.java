@Override
protected void reset(long cPtr, boolean cMemoryOwn) {
    if (!destroyed)
        destroy();
    super.reset(CollisionJNI.SphereTriangleDetector_SWIGUpcast(swigCPtr = cPtr), cMemoryOwn);
}
