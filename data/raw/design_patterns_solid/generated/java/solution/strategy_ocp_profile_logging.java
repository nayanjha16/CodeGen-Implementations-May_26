// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=profile | tier=logging
package org.example.patterns;

interface ProfileStrategy {
    int apply(int amount);
}

class ProfileNormalStrategy implements ProfileStrategy {
    public int apply(int amount) { return amount; }
}

class ProfileDiscountStrategy implements ProfileStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class ProfileContext {
    private ProfileStrategy strategy;
    public ProfileContext(ProfileStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(ProfileStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "profile-strategy"; }
}
