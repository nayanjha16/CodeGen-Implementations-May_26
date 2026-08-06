// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=session | tier=errors
package org.example.patterns;

interface SessionImpl {
    String write(String msg);
}

class SessionFileImpl implements SessionImpl {
    public String write(String msg) { return "file:session:" + msg; }
}

class SessionMemoryImpl implements SessionImpl {
    public String write(String msg) { return "mem:session:" + msg; }
}

public abstract class SessionBridge {
    protected final SessionImpl impl;
    protected SessionBridge(SessionImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class SessionAlertBridge extends SessionBridge {
    public SessionAlertBridge(SessionImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
