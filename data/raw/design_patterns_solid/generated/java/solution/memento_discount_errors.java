// DesignPatternsSolid | kind=design_pattern | label=memento | domain=discount | tier=errors
package org.example.patterns;

public class DiscountMemento {
    private final String state;
    public DiscountMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class DiscountOriginator {
    private String state = "discount-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public DiscountMemento save() { return new DiscountMemento(state); }
    public void restore(DiscountMemento m) { this.state = m.getState(); }
}
