// DesignPatternsSolid | kind=design_pattern | label=memento | domain=http | tier=errors
package org.example.patterns;

public class HttpMemento {
    private final String state;
    public HttpMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class HttpOriginator {
    private String state = "http-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public HttpMemento save() { return new HttpMemento(state); }
    public void restore(HttpMemento m) { this.state = m.getState(); }
}
