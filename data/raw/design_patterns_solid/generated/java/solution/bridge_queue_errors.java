// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=queue | tier=errors
package org.example.patterns;

interface QueueImpl {
    String write(String msg);
}

class QueueFileImpl implements QueueImpl {
    public String write(String msg) { return "file:queue:" + msg; }
}

class QueueMemoryImpl implements QueueImpl {
    public String write(String msg) { return "mem:queue:" + msg; }
}

public abstract class QueueBridge {
    protected final QueueImpl impl;
    protected QueueBridge(QueueImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class QueueAlertBridge extends QueueBridge {
    public QueueAlertBridge(QueueImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
