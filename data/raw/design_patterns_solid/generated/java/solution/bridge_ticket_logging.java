// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=ticket | tier=logging
package org.example.patterns;

interface TicketImpl {
    String write(String msg);
}

class TicketFileImpl implements TicketImpl {
    public String write(String msg) { return "file:ticket:" + msg; }
}

class TicketMemoryImpl implements TicketImpl {
    public String write(String msg) { return "mem:ticket:" + msg; }
}

public abstract class TicketBridge {
    protected final TicketImpl impl;
    protected TicketBridge(TicketImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class TicketAlertBridge extends TicketBridge {
    public TicketAlertBridge(TicketImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
