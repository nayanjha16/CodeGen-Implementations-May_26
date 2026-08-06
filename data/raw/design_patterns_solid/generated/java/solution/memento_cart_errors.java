// DesignPatternsSolid | kind=design_pattern | label=memento | domain=cart | tier=errors
package org.example.patterns;

public class CartMemento {
    private final String state;
    public CartMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class CartOriginator {
    private String state = "cart-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public CartMemento save() { return new CartMemento(state); }
    public void restore(CartMemento m) { this.state = m.getState(); }
}
