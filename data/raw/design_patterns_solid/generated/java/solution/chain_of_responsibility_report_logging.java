// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=report | tier=logging
package org.example.patterns;

public abstract class ReportHandler {
    protected ReportHandler next;
    public ReportHandler link(ReportHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-report";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class ReportLowHandler extends ReportHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-report:" + msg; }
}

class ReportHighHandler extends ReportHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-report:" + msg; }
}
