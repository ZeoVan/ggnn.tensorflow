public btTransformFloatData getRbBFrame() {
    long cPtr = DynamicsJNI.btSliderConstraintData_rbBFrame_get(swigCPtr, this);
    return (cPtr == 0) ? null : new btTransformFloatData(cPtr, false);
}
