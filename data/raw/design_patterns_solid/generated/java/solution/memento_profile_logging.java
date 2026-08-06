// DesignPatternsSolid | kind=design_pattern | label=memento | domain=profile | tier=logging
package org.example.patterns;

public class ProfileMemento {
    private final String state;
    public ProfileMemento(String state) { this.state = state; }
    public String getState() { return state; }
}

class ProfileOriginator {
    private String state = "profile-init";
    public void setState(String state) { this.state = state; }
    public String getState() { return state; }
    public ProfileMemento save() { return new ProfileMemento(state); }
    public void restore(ProfileMemento m) { this.state = m.getState(); }
}
