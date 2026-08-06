// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=email | tier=minimal
package org.example.patterns;

interface EmailImpl {
    String write(String msg);
}

class EmailFileImpl implements EmailImpl {
    public String write(String msg) { return "file:email:" + msg; }
}

class EmailMemoryImpl implements EmailImpl {
    public String write(String msg) { return "mem:email:" + msg; }
}

public abstract class EmailBridge {
    protected final EmailImpl impl;
    protected EmailBridge(EmailImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class EmailAlertBridge extends EmailBridge {
    public EmailAlertBridge(EmailImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
