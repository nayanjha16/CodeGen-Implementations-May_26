// DesignPatternsSolid | kind=design_pattern | label=memento | domain=plugin | tier=minimal
package org.example.patterns;

public class PluginMemento {
    private final String state;
    public PluginMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class PluginOriginator {
    private String state = "plugin-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public PluginMemento save() { return new PluginMemento(state); }
    public void restore(PluginMemento m) { this.state = m.getState(); }
}
