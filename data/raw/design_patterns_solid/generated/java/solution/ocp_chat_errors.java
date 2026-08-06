// DesignPatternsSolid | kind=solid | label=ocp | domain=chat | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface ChatDiscount {
    int apply(int price);
}

class ChatNoDiscount implements ChatDiscount {
    public int apply(int price) { return price; }
}

class ChatTenPercent implements ChatDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class ChatPriceEngine {
    private final ChatDiscount discount;
    public ChatPriceEngine(ChatDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "chat"; }
}
