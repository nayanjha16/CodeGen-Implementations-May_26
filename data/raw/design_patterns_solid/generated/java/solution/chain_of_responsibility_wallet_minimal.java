// DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=wallet | tier=minimal
package org.example.patterns;

public abstract class WalletHandler {
    protected WalletHandler next;
    public WalletHandler link(WalletHandler n) { next = n; return n; }
    public String handle(int level, String msg) {
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-wallet";
    }
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}

class WalletLowHandler extends WalletHandler {
    protected boolean canHandle(int level) { return level <= 1; }
    protected String doHandle(String msg) { return "low-wallet:" + msg; }
}

class WalletHighHandler extends WalletHandler {
    protected boolean canHandle(int level) { return level > 1; }
    protected String doHandle(String msg) { return "high-wallet:" + msg; }
}
