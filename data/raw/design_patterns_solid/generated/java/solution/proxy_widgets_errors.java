// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=widgets | tier=errors
package org.example.patterns;

interface WidgetsService {
    String load(String id);
}

class WidgetsRealService implements WidgetsService {
    public String load(String id) { return "real-widgets:" + id; }
}

public class WidgetsProxy implements WidgetsService {
    private WidgetsRealService real;
    private final boolean allowed;
    public WidgetsProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new WidgetsRealService();
        return real.load(id);
    }
}
