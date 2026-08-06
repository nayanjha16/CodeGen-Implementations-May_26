// DesignPatternsSolid | kind=design_pattern | label=memento | domain=tax | tier=errors
package org.example.patterns;

public class TaxMemento {
    private final String state;
    public TaxMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class TaxOriginator {
    private String state = "tax-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public TaxMemento save() { return new TaxMemento(state); }
    public void restore(TaxMemento m) { this.state = m.getState(); }
}
