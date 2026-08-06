// DesignPatternsSolid | kind=design_pattern | label=command | domain=sms | tier=logging
package org.example.patterns;

interface SmsCommand {
    String execute();
}

class SmsReceiver {
    public String action(String x) { return "done-sms:" + x; }
}

public class SmsActionCommand implements SmsCommand {
    private final SmsReceiver receiver;
    private final String payload;
    public SmsActionCommand(SmsReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
