// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=inventory | tier=errors
package org.example.patterns;

interface InventoryImpl {
    String write(String msg);
}

class InventoryFileImpl implements InventoryImpl {
    public String write(String msg) { return "file:inventory:" + msg; }
}

class InventoryMemoryImpl implements InventoryImpl {
    public String write(String msg) { return "mem:inventory:" + msg; }
}

public abstract class InventoryBridge {
    protected final InventoryImpl impl;
    protected InventoryBridge(InventoryImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class InventoryAlertBridge extends InventoryBridge {
    public InventoryAlertBridge(InventoryImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
