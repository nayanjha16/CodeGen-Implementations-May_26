// DesignPatternsSolid | kind=design_pattern | label=command | domain=license | tier=minimal
package org.example.patterns;

interface LicenseCommand {
    String execute();
}

class LicenseReceiver {
    public String action(String x) { return "done-license:" + x; }
}

public class LicenseActionCommand implements LicenseCommand {
    private final LicenseReceiver receiver;
    private final String payload;
    public LicenseActionCommand(LicenseReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
