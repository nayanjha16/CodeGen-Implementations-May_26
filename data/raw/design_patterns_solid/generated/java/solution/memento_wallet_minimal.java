// DesignPatternsSolid | kind=design_pattern | label=memento | domain=wallet | tier=minimal
package org.example.patterns;

public class WalletMemento {
    private final String state;
    public WalletMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class WalletOriginator {
    private String state = "wallet-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public WalletMemento save() { return new WalletMemento(state); }
    public void restore(WalletMemento m) { this.state = m.getState(); }
}
