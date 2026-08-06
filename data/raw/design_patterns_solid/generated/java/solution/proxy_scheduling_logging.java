// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=scheduling | tier=logging
package org.example.patterns;

interface SchedulingService {
    String load(String id);
}

class SchedulingRealService implements SchedulingService {
    public String load(String id) { return "real-scheduling:" + id; }
}

public class SchedulingProxy implements SchedulingService {
    private SchedulingRealService real;
    private final boolean allowed;
    public SchedulingProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new SchedulingRealService();
        return real.load(id);
    }
}
