@Override
protected void reset(long cPtr, boolean cMemoryOwn) {
    if (!destroyed)
        destroy();
    super.reset(DynamicsJNI.btHinge2Constraint_SWIGUpcast(swigCPtr = cPtr), cMemoryOwn);
}
