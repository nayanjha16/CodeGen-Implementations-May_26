// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=comment | tier=logging
package org.example.patterns;

interface CommentStrategy {
    int apply(int amount);
}

class CommentNormalStrategy implements CommentStrategy {
    public int apply(int amount) { return amount; }
}

class CommentDiscountStrategy implements CommentStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class CommentContext {
    private CommentStrategy strategy;
    public CommentContext(CommentStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(CommentStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "comment-strategy"; }
}
