// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=auth | tier=minimal
package org.example.patterns;

interface AuthStrategy {
    int apply(int amount);
}

class AuthNormalStrategy implements AuthStrategy {
    public int apply(int amount) { return amount; }
}

class AuthDiscountStrategy implements AuthStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class AuthContext {
    private AuthStrategy strategy;
    public AuthContext(AuthStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(AuthStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "auth-strategy"; }
}
