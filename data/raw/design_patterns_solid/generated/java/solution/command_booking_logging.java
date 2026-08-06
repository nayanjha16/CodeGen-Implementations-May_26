// DesignPatternsSolid | kind=design_pattern | label=command | domain=booking | tier=logging
package org.example.patterns;

interface BookingCommand {
    String execute();
}

class BookingReceiver {
    public String action(String x) { return "done-booking:" + x; }
}

public class BookingActionCommand implements BookingCommand {
    private final BookingReceiver receiver;
    private final String payload;
    public BookingActionCommand(BookingReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
