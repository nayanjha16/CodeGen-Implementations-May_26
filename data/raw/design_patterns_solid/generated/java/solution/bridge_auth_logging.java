// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=auth | tier=logging
package org.example.patterns;

interface AuthImpl {
    String write(String msg);
}

class AuthFileImpl implements AuthImpl {
    public String write(String msg) { return "file:auth:" + msg; }
}

class AuthMemoryImpl implements AuthImpl {
    public String write(String msg) { return "mem:auth:" + msg; }
}

public abstract class AuthBridge {
    protected final AuthImpl impl;
    protected AuthBridge(AuthImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class AuthAlertBridge extends AuthBridge {
    public AuthAlertBridge(AuthImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
