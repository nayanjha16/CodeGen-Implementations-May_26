// DesignPatternsSolid | kind=design_pattern | label=command | domain=calendar | tier=errors
package org.example.patterns;

interface CalendarCommand {
    String execute();
}

class CalendarReceiver {
    public String action(String x) { return "done-calendar:" + x; }
}

public class CalendarActionCommand implements CalendarCommand {
    private final CalendarReceiver receiver;
    private final String payload;
    public CalendarActionCommand(CalendarReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
