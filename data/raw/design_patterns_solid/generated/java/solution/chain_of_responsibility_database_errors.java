// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=database | tier=errors
package org.example.patterns;

public abstract class DatabaseHandler {
    protected DatabaseHandler next;
    public DatabaseHandler link(DatabaseHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-database";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class DatabaseLowHandler extends DatabaseHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-database:" + msg; }
}

class DatabaseHighHandler extends DatabaseHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-database:" + msg; }
}
