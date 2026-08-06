// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=notes | tier=minimal
package org.example.patterns;

interface NotesStrategy {
    int apply(int amount);
}

class NotesNormalStrategy implements NotesStrategy {
    public int apply(int amount) { return amount; }
}

class NotesDiscountStrategy implements NotesStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class NotesContext {
    private NotesStrategy strategy;
    public NotesContext(NotesStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(NotesStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "notes-strategy"; }
}
