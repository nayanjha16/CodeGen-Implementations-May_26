// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=metrics | tier=logging
package org.example.patterns;

public abstract class MetricsHandler {
    protected MetricsHandler next;
    public MetricsHandler link(MetricsHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-metrics";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class MetricsLowHandler extends MetricsHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-metrics:" + msg; }
}

class MetricsHighHandler extends MetricsHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-metrics:" + msg; }
}
