public void setStopERP(btVector3 value) {
    DynamicsJNI.btTranslationalLimitMotor_stopERP_set(swigCPtr, this, btVector3.getCPtr(value), value);
}
