// DesignPatternsSolid | kind=design_pattern | label=memento | domain=cache | tier=minimal
package org.example.patterns;

public class CacheMemento {
    private final String state;
    public CacheMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class CacheOriginator {
    private String state = "cache-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public CacheMemento save() { return new CacheMemento(state); }
    public void restore(CacheMemento m) { this.state = m.getState(); }
}
