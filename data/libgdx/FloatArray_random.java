/**
 * Returns a random item from the array, or zero if the array is empty.
 */
public float random() {
    if (size == 0)
        return 0;
    return items[MathUtils.random(0, size - 1)];
}
