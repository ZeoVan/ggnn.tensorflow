@Override
protected void reset(long cPtr, boolean cMemoryOwn) {
    if (!destroyed)
        destroy();
    super.reset(CollisionJNI.btCompoundCollisionAlgorithm_SwappedCreateFunc_SWIGUpcast(swigCPtr = cPtr), cMemoryOwn);
}
