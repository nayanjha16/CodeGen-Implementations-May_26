// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=queue | tier=minimal
package org.example.patterns;

interface QueueService {
    String load(String id);
}

class QueueRealService implements QueueService {
    public String load(String id) { return "real-queue:" + id; }
}

public class QueueProxy implements QueueService {
    private QueueRealService real;
    private final boolean allowed;
    public QueueProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new QueueRealService();
        return real.load(id);
    }
}
