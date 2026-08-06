// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=comment | tier=logging
package org.example.patterns;

public abstract class CommentHandler {
    protected CommentHandler next;
    public CommentHandler link(CommentHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-comment";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class CommentLowHandler extends CommentHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-comment:" + msg; }
}

class CommentHighHandler extends CommentHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-comment:" + msg; }
}
