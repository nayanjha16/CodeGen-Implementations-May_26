// DesignPatternsSolid | kind=design_pattern | label=command | domain=payments | tier=errors
package org.example.patterns;

interface PaymentsCommand {
    String execute();
}

class PaymentsReceiver {
    public String action(String x) { return "done-payments:" + x; }
}

public class PaymentsActionCommand implements PaymentsCommand {
    private final PaymentsReceiver receiver;
    private final String payload;
    public PaymentsActionCommand(PaymentsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
