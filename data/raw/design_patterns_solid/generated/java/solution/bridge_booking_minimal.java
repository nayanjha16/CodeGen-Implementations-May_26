// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=booking | tier=minimal
package org.example.patterns;

interface BookingImpl {
    String write(String msg);
}

class BookingFileImpl implements BookingImpl {
    public String write(String msg) { return "file:booking:" + msg; }
}

class BookingMemoryImpl implements BookingImpl {
    public String write(String msg) { return "mem:booking:" + msg; }
}

public abstract class BookingBridge {
    protected final BookingImpl impl;
    protected BookingBridge(BookingImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class BookingAlertBridge extends BookingBridge {
    public BookingAlertBridge(BookingImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
