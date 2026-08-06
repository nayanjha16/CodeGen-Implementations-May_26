// DesignPatternsSolid | kind=design_pattern | label=memento | domain=video | tier=minimal
package org.example.patterns;

public class VideoMemento {
    private final String state;
    public VideoMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class VideoOriginator {
    private String state = "video-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public VideoMemento save() { return new VideoMemento(state); }
    public void restore(VideoMemento m) { this.state = m.getState(); }
}
