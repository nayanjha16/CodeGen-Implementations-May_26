// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=queue | tier=logging
package org.example.patterns;

interface QueueStrategy {
    int apply(int amount);
}

class QueueNormalStrategy implements QueueStrategy {
    public int apply(int amount) { return amount; }
}

class QueueDiscountStrategy implements QueueStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class QueueContext {
    private QueueStrategy strategy;
    public QueueContext(QueueStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(QueueStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "queue-strategy"; }
}
