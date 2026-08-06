// DesignPatternsSolid | kind=design_pattern | label=memento | domain=audio | tier=minimal
package org.example.patterns;

public class AudioMemento {
    private final String state;
    public AudioMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class AudioOriginator {
    private String state = "audio-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public AudioMemento save() { return new AudioMemento(state); }
    public void restore(AudioMemento m) { this.state = m.getState(); }
}
