// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=config | tier=errors
package org.example.patterns;

public abstract class ConfigHandler {
    protected ConfigHandler next;
    public ConfigHandler link(ConfigHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-config";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class ConfigLowHandler extends ConfigHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-config:" + msg; }
}

class ConfigHighHandler extends ConfigHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-config:" + msg; }
}
