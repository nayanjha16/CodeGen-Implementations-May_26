// DesignPatternsSolid | kind=design_pattern | label=memento | domain=report | tier=logging
package org.example.patterns;

public class ReportMemento {
    private final String state;
    public ReportMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class ReportOriginator {
    private String state = "report-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public ReportMemento save() { return new ReportMemento(state); }
    public void restore(ReportMemento m) { this.state = m.getState(); }
}
