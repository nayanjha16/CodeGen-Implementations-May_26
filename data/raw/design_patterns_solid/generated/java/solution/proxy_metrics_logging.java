// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=metrics | tier=logging
package org.example.patterns;

interface MetricsService {
    String load(String id);
}

class MetricsRealService implements MetricsService {
    public String load(String id) { return "real-metrics:" + id; }
}

public class MetricsProxy implements MetricsService {
    private MetricsRealService real;
    private final boolean allowed;
    public MetricsProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new MetricsRealService();
        return real.load(id);
    }
}
