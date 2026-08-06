// DesignPatternsSolid | kind=design_pattern | label=command | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletCommand {
    String execute();
}

class WalletReceiver {
    public String action(String x) { return "done-wallet:" + x; }
}

public class WalletActionCommand implements WalletCommand {
    private final WalletReceiver receiver;
    private final String payload;
    public WalletActionCommand(WalletReceiver r, String payload) {
        this.receiver = r; this.payload = payload;
    }
    public String execute() { return receiver.action(payload); }
}
