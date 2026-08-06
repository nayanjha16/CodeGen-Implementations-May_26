// DesignPatternsSolid | kind=solid | label=ocp | domain=todo | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface TodoDiscount {
    int apply(int price);
}

class TodoNoDiscount implements TodoDiscount {
    public int apply(int price) { return price; }
}

class TodoTenPercent implements TodoDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class TodoPriceEngine {
    private final TodoDiscount discount;
    public TodoPriceEngine(TodoDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "todo"; }
}
