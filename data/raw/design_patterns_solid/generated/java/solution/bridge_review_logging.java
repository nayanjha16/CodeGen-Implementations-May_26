// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=review | tier=logging
package org.example.patterns;

interface ReviewImpl {
    String write(String msg);
}

class ReviewFileImpl implements ReviewImpl {
    public String write(String msg) { return "file:review:" + msg; }
}

class ReviewMemoryImpl implements ReviewImpl {
    public String write(String msg) { return "mem:review:" + msg; }
}

public abstract class ReviewBridge {
    protected final ReviewImpl impl;
    protected ReviewBridge(ReviewImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class ReviewAlertBridge extends ReviewBridge {
    public ReviewAlertBridge(ReviewImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
