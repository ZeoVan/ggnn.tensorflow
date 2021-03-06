public void addAll(long[] array, int offset, int length) {
    long[] items = this.items;
    int sizeNeeded = size + length;
    if (sizeNeeded > items.length)
        items = resize(Math.max(8, (int) (sizeNeeded * 1.75f)));
    System.arraycopy(array, offset, items, size, length);
    size += length;
}
