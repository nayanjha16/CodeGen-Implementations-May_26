// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletService {
    String load(String id);
}

class WalletRealService implements WalletService {
    public String load(String id) { return "real-wallet:" + id; }
}

public class WalletProxy implements WalletService {
    private WalletRealService real;
    private final boolean allowed;
    public WalletProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new WalletRealService();
        return real.load(id);
    }
}
