// DesignPatternsSolid | kind=solid | label=srp | domain=wallet | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for wallet
class WalletRecord {
    public final String id;
    public final int amount;
    public WalletRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class WalletRepository {
    public String save(WalletRecord r) { return "saved-wallet:" + r.id; }
}

public class WalletFormatter {
    public String format(WalletRecord r) { return r.id + "=" + r.amount; }
}
