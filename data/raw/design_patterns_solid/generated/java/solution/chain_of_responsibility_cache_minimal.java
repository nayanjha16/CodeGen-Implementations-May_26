// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=cache | tier=minimal
package org.example.patterns;

public abstract class CacheHandler {
    protected CacheHandler next;
    public CacheHandler link(CacheHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-cache";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class CacheLowHandler extends CacheHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-cache:" + msg; }
}

class CacheHighHandler extends CacheHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-cache:" + msg; }
}
