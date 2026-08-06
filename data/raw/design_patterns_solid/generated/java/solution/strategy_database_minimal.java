// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=database | tier=minimal
package org.example.patterns;

interface DatabaseStrategy {
    int apply(int amount);
}

class DatabaseNormalStrategy implements DatabaseStrategy {
    public int apply(int amount) { return amount; }
}

class DatabaseDiscountStrategy implements DatabaseStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class DatabaseContext {
    private DatabaseStrategy strategy;
    public DatabaseContext(DatabaseStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(DatabaseStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "database-strategy"; }
}
