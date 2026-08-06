// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=todo | tier=minimal
package org.example.patterns;

interface TodoImpl {
    String write(String msg);
}

class TodoFileImpl implements TodoImpl {
    public String write(String msg) { return "file:todo:" + msg; }
}

class TodoMemoryImpl implements TodoImpl {
    public String write(String msg) { return "mem:todo:" + msg; }
}

public abstract class TodoBridge {
    protected final TodoImpl impl;
    protected TodoBridge(TodoImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class TodoAlertBridge extends TodoBridge {
    public TodoAlertBridge(TodoImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
