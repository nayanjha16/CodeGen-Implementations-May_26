// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=license | tier=logging
package org.example.patterns;

interface LicenseStrategy {
    int apply(int amount);
}

class LicenseNormalStrategy implements LicenseStrategy {
    public int apply(int amount) { return amount; }
}

class LicenseDiscountStrategy implements LicenseStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class LicenseContext {
    private LicenseStrategy strategy;
    public LicenseContext(LicenseStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(LicenseStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "license-strategy"; }
}
