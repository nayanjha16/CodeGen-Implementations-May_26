// DesignPatternsSolid | kind=design_pattern | label=memento | domain=metrics | tier=minimal
package org.example.patterns;

public class MetricsMemento {
    private final String state;
    public MetricsMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class MetricsOriginator {
    private String state = "metrics-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public MetricsMemento save() { return new MetricsMemento(state); }
    public void restore(MetricsMemento m) { this.state = m.getState(); }
}
