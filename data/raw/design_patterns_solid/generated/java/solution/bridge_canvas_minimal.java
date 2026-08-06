// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=canvas | tier=minimal
package org.example.patterns;

interface CanvasImpl {
    String write(String msg);
}

class CanvasFileImpl implements CanvasImpl {
    public String write(String msg) { return "file:canvas:" + msg; }
}

class CanvasMemoryImpl implements CanvasImpl {
    public String write(String msg) { return "mem:canvas:" + msg; }
}

public abstract class CanvasBridge {
    protected final CanvasImpl impl;
    protected CanvasBridge(CanvasImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class CanvasAlertBridge extends CanvasBridge {
    public CanvasAlertBridge(CanvasImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
