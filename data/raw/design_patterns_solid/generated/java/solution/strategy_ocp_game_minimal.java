// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=game | tier=minimal
package org.example.patterns;

interface GameStrategy {
    int apply(int amount);
}

class GameNormalStrategy implements GameStrategy {
    public int apply(int amount) { return amount; }
}

class GameDiscountStrategy implements GameStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class GameContext {
    private GameStrategy strategy;
    public GameContext(GameStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(GameStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "game-strategy"; }
}
