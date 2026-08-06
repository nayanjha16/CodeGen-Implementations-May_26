// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=logging | tier=minimal
package org.example.patterns;

interface LoggingService {
    String load(String id);
}

class LoggingRealService implements LoggingService {
    public String load(String id) { return "real-logging:" + id; }
}

public class LoggingProxy implements LoggingService {
    private LoggingRealService real;
    private final boolean allowed;
    public LoggingProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new LoggingRealService();
        return real.load(id);
    }
}
