// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=chat | tier=logging
package org.example.patterns;

public abstract class ChatHandler {
    protected ChatHandler next;
    public ChatHandler link(ChatHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-chat";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class ChatLowHandler extends ChatHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-chat:" + msg; }
}

class ChatHighHandler extends ChatHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-chat:" + msg; }
}
