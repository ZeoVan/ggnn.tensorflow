@Override
protected void reset(long cPtr, boolean cMemoryOwn) {
    if (!destroyed)
        destroy();
    super.reset(CollisionJNI.btSphereBoxCollisionAlgorithm_CreateFunc_SWIGUpcast(swigCPtr = cPtr), cMemoryOwn);
}
