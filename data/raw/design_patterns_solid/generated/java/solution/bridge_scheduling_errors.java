// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=scheduling | tier=errors
package org.example.patterns;

interface SchedulingImpl {
    String write(String msg);
}

class SchedulingFileImpl implements SchedulingImpl {
    public String write(String msg) { return "file:scheduling:" + msg; }
}

class SchedulingMemoryImpl implements SchedulingImpl {
    public String write(String msg) { return "mem:scheduling:" + msg; }
}

public abstract class SchedulingBridge {
    protected final SchedulingImpl impl;
    protected SchedulingBridge(SchedulingImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class SchedulingAlertBridge extends SchedulingBridge {
    public SchedulingAlertBridge(SchedulingImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
