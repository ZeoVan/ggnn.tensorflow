/**
 * Removes from this array all of elements contained in the specified array.
 * @return true if this array was modified.
 */
public boolean removeAll(ShortArray array) {
    int size = this.size;
    int startSize = size;
    short[] items = this.items;
    for (int i = 0, n = array.size; i < n; i++) {
        short item = array.get(i);
        for (int ii = 0; ii < size; ii++) {
            if (item == items[ii]) {
                removeIndex(ii);
                size--;
                break;
            }
        }
    }
    return size != startSize;
}
