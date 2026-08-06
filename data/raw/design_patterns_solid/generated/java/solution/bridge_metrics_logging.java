// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=metrics | tier=logging
package org.example.patterns;

interface MetricsImpl {
    String write(String msg);
}

class MetricsFileImpl implements MetricsImpl {
    public String write(String msg) { return "file:metrics:" + msg; }
}

class MetricsMemoryImpl implements MetricsImpl {
    public String write(String msg) { return "mem:metrics:" + msg; }
}

public abstract class MetricsBridge {
    protected final MetricsImpl impl;
    protected MetricsBridge(MetricsImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class MetricsAlertBridge extends MetricsBridge {
    public MetricsAlertBridge(MetricsImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
