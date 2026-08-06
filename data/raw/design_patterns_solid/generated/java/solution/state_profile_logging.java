// DesignPatternsSolid | kind=design_pattern | label=state | domain=profile | tier=logging
package org.example.patterns;

interface ProfileState {
    String handle(ProfileContext ctx);
}

class ProfileOnState implements ProfileState {
    public String handle(ProfileContext ctx) {
        ctx.setState(new ProfileOffState());
        return "was-on-profile";
    }
}

class ProfileOffState implements ProfileState {
    public String handle(ProfileContext ctx) {
        ctx.setState(new ProfileOnState());
        return "was-off-profile";
    }
}

public class ProfileContext {
    private ProfileState state = new ProfileOffState();
    public void setState(ProfileState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
