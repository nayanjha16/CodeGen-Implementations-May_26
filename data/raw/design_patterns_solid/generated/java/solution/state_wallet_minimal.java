// DesignPatternsSolid | kind=design_pattern | label=state | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletState {
    String handle(WalletContext ctx);
}

class WalletOnState implements WalletState {
    public String handle(WalletContext ctx) {
        ctx.setState(new WalletOffState());
        return "was-on-wallet";
    }
}

class WalletOffState implements WalletState {
    public String handle(WalletContext ctx) {
        ctx.setState(new WalletOnState());
        return "was-off-wallet";
    }
}

public class WalletContext {
    private WalletState state = new WalletOffState();
    public void setState(WalletState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
