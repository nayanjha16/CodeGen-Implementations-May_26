// DesignPatternsSolid | kind=design_pattern | label=memento | domain=shipping | tier=logging
package org.example.patterns;

public class ShippingMemento {
    private final String state;
    public ShippingMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class ShippingOriginator {
    private String state = "shipping-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public ShippingMemento save() { return new ShippingMemento(state); }
    public void restore(ShippingMemento m) { this.state = m.getState(); }
}
