public btVector3 getMVertices() {
    long cPtr = LinearMathJNI.HullDesc_mVertices_get(swigCPtr, this);
    return (cPtr == 0) ? null : new btVector3(cPtr, false);
}
