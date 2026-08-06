// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=calendar | tier=errors
package org.example.patterns;

interface CalendarImpl {
    String write(String msg);
}

class CalendarFileImpl implements CalendarImpl {
    public String write(String msg) { return "file:calendar:" + msg; }
}

class CalendarMemoryImpl implements CalendarImpl {
    public String write(String msg) { return "mem:calendar:" + msg; }
}

public abstract class CalendarBridge {
    protected final CalendarImpl impl;
    protected CalendarBridge(CalendarImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class CalendarAlertBridge extends CalendarBridge {
    public CalendarAlertBridge(CalendarImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
