// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=feed | tier=logging
package org.example.patterns;

public abstract class FeedHandler {
    protected FeedHandler next;
    public FeedHandler link(FeedHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-feed";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class FeedLowHandler extends FeedHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-feed:" + msg; }
}

class FeedHighHandler extends FeedHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-feed:" + msg; }
}
