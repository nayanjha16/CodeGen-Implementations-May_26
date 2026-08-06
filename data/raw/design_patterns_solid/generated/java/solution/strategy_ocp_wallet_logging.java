// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=wallet | tier=logging
package org.example.patterns;

interface WalletStrategy {
    int apply(int amount);
}

class WalletNormalStrategy implements WalletStrategy {
    public int apply(int amount) { return amount; }
}

class WalletDiscountStrategy implements WalletStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class WalletContext {
    private WalletStrategy strategy;
    public WalletContext(WalletStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(WalletStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "wallet-strategy"; }
}
