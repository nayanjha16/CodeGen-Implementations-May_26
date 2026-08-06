// DesignPatternsSolid | kind=design_pattern | label=memento | domain=streaming | tier=errors
package org.example.patterns;

public class StreamingMemento {
    private final String state;
    public StreamingMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class StreamingOriginator {
    private String state = "streaming-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public StreamingMemento save() { return new StreamingMemento(state); }
    public void restore(StreamingMemento m) { this.state = m.getState(); }
}
