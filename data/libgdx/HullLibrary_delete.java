@Override
protected synchronized void delete() {
    if (swigCPtr != 0) {
        if (swigCMemOwn) {
            swigCMemOwn = false;
            LinearMathJNI.delete_HullLibrary(swigCPtr);
        }
        swigCPtr = 0;
    }
    super.delete();
}
