// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=chat | tier=logging
package org.example.patterns;

interface ChatStrategy {
    int apply(int amount);
}

class ChatNormalStrategy implements ChatStrategy {
    public int apply(int amount) { return amount; }
}

class ChatDiscountStrategy implements ChatStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class ChatContext {
    private ChatStrategy strategy;
    public ChatContext(ChatStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(ChatStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "chat-strategy"; }
}
