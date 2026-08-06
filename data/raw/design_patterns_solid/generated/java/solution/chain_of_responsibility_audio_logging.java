// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=audio | tier=logging
package org.example.patterns;

public abstract class AudioHandler {
    protected AudioHandler next;
    public AudioHandler link(AudioHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-audio";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class AudioLowHandler extends AudioHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-audio:" + msg; }
}

class AudioHighHandler extends AudioHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-audio:" + msg; }
}
