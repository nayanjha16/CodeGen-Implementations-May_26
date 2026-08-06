// DesignPatternsSolid | kind=design_pattern | label=memento | domain=analytics | tier=minimal
package org.example.patterns;

public class AnalyticsMemento {
    private final String state;
    public AnalyticsMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class AnalyticsOriginator {
    private String state = "analytics-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public AnalyticsMemento save() { return new AnalyticsMemento(state); }
    public void restore(AnalyticsMemento m) { this.state = m.getState(); }
}
