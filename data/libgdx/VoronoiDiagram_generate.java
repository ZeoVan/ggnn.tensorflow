public void generate(float radius) {
    assert (m_diagram == null);
    float inverseRadius = 1 / radius;
    lower.x = Float.MAX_VALUE;
    lower.y = Float.MAX_VALUE;
    upper.x = -Float.MAX_VALUE;
    upper.y = -Float.MAX_VALUE;
    for (int k = 0; k < m_generatorCount; k++) {
        Generator g = m_generatorBuffer[k];
        Vec2.minToOut(lower, g.center, lower);
        Vec2.maxToOut(upper, g.center, upper);
    }
    m_countX = 1 + (int) (inverseRadius * (upper.x - lower.x));
    m_countY = 1 + (int) (inverseRadius * (upper.y - lower.y));
    m_diagram = new Generator[m_countX * m_countY];
    queue.reset(new VoronoiDiagramTask[4 * m_countX * m_countX]);
    for (int k = 0; k < m_generatorCount; k++) {
        Generator g = m_generatorBuffer[k];
        g.center.x = inverseRadius * (g.center.x - lower.x);
        g.center.y = inverseRadius * (g.center.y - lower.y);
        int x = MathUtils.max(0, MathUtils.min((int) g.center.x, m_countX - 1));
        int y = MathUtils.max(0, MathUtils.min((int) g.center.y, m_countY - 1));
        queue.push(taskPool.pop().set(x, y, x + y * m_countX, g));
    }
    while (!queue.empty()) {
        VoronoiDiagramTask front = queue.pop();
        int x = front.m_x;
        int y = front.m_y;
        int i = front.m_i;
        Generator g = front.m_generator;
        if (m_diagram[i] == null) {
            m_diagram[i] = g;
            if (x > 0) {
                queue.push(taskPool.pop().set(x - 1, y, i - 1, g));
            }
            if (y > 0) {
                queue.push(taskPool.pop().set(x, y - 1, i - m_countX, g));
            }
            if (x < m_countX - 1) {
                queue.push(taskPool.pop().set(x + 1, y, i + 1, g));
            }
            if (y < m_countY - 1) {
                queue.push(taskPool.pop().set(x, y + 1, i + m_countX, g));
            }
        }
        taskPool.push(front);
    }
    int maxIteration = m_countX + m_countY;
    for (int iteration = 0; iteration < maxIteration; iteration++) {
        for (int y = 0; y < m_countY; y++) {
            for (int x = 0; x < m_countX - 1; x++) {
                int i = x + y * m_countX;
                Generator a = m_diagram[i];
                Generator b = m_diagram[i + 1];
                if (a != b) {
                    queue.push(taskPool.pop().set(x, y, i, b));
                    queue.push(taskPool.pop().set(x + 1, y, i + 1, a));
                }
            }
        }
        for (int y = 0; y < m_countY - 1; y++) {
            for (int x = 0; x < m_countX; x++) {
                int i = x + y * m_countX;
                Generator a = m_diagram[i];
                Generator b = m_diagram[i + m_countX];
                if (a != b) {
                    queue.push(taskPool.pop().set(x, y, i, b));
                    queue.push(taskPool.pop().set(x, y + 1, i + m_countX, a));
                }
            }
        }
        boolean updated = false;
        while (!queue.empty()) {
            VoronoiDiagramTask front = queue.pop();
            int x = front.m_x;
            int y = front.m_y;
            int i = front.m_i;
            Generator k = front.m_generator;
            Generator a = m_diagram[i];
            Generator b = k;
            if (a != b) {
                float ax = a.center.x - x;
                float ay = a.center.y - y;
                float bx = b.center.x - x;
                float by = b.center.y - y;
                float a2 = ax * ax + ay * ay;
                float b2 = bx * bx + by * by;
                if (a2 > b2) {
                    m_diagram[i] = b;
                    if (x > 0) {
                        queue.push(taskPool.pop().set(x - 1, y, i - 1, b));
                    }
                    if (y > 0) {
                        queue.push(taskPool.pop().set(x, y - 1, i - m_countX, b));
                    }
                    if (x < m_countX - 1) {
                        queue.push(taskPool.pop().set(x + 1, y, i + 1, b));
                    }
                    if (y < m_countY - 1) {
                        queue.push(taskPool.pop().set(x, y + 1, i + m_countX, b));
                    }
                    updated = true;
                }
            }
            taskPool.push(front);
        }
        if (!updated) {
            break;
        }
    }
}
