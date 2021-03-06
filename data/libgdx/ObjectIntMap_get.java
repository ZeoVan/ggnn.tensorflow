/**
 * @param defaultValue Returned if the key was not associated with a value.
 */
public int get(K key, int defaultValue) {
    int hashCode = key.hashCode();
    int index = hashCode & mask;
    if (!key.equals(keyTable[index])) {
        index = hash2(hashCode);
        if (!key.equals(keyTable[index])) {
            index = hash3(hashCode);
            if (!key.equals(keyTable[index]))
                return getStash(key, defaultValue);
        }
    }
    return valueTable[index];
}
