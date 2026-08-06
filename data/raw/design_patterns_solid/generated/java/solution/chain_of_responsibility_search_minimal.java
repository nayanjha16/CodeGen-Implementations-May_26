// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=search | tier=minimal
package org.example.patterns;

public abstract class SearchHandler {
    protected SearchHandler next;
    public SearchHandler link(SearchHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-search";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class SearchLowHandler extends SearchHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-search:" + msg; }
}

class SearchHighHandler extends SearchHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-search:" + msg; }
}
