// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=sensors | tier=minimal
package org.example.patterns;

interface SensorsService {
    String load(String id);
}

class SensorsRealService implements SensorsService {
    public String load(String id) { return "real-sensors:" + id; }
}

public class SensorsProxy implements SensorsService {
    private SensorsRealService real;
    private final boolean allowed;
    public SensorsProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new SensorsRealService();
        return real.load(id);
    }
}
