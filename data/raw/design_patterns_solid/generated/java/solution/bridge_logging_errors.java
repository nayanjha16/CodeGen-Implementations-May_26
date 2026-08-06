// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=logging | tier=errors
package org.example.patterns;

interface LoggingImpl {
    String write(String msg);
}

class LoggingFileImpl implements LoggingImpl {
    public String write(String msg) { return "file:logging:" + msg; }
}

class LoggingMemoryImpl implements LoggingImpl {
    public String write(String msg) { return "mem:logging:" + msg; }
}

public abstract class LoggingBridge {
    protected final LoggingImpl impl;
    protected LoggingBridge(LoggingImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class LoggingAlertBridge extends LoggingBridge {
    public LoggingAlertBridge(LoggingImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
