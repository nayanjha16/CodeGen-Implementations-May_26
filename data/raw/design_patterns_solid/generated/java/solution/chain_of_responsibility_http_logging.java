// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=http | tier=logging
package org.example.patterns;

public abstract class HttpHandler {
    protected HttpHandler next;
    public HttpHandler link(HttpHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-http";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class HttpLowHandler extends HttpHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-http:" + msg; }
}

class HttpHighHandler extends HttpHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-http:" + msg; }
}
