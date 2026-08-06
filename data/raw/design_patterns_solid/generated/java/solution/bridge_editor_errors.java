// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=editor | tier=errors
package org.example.patterns;

interface EditorImpl {
    String write(String msg);
}

class EditorFileImpl implements EditorImpl {
    public String write(String msg) { return "file:editor:" + msg; }
}

class EditorMemoryImpl implements EditorImpl {
    public String write(String msg) { return "mem:editor:" + msg; }
}

public abstract class EditorBridge {
    protected final EditorImpl impl;
    protected EditorBridge(EditorImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class EditorAlertBridge extends EditorBridge {
    public EditorAlertBridge(EditorImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
