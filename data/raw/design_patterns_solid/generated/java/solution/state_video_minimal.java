// DesignPatternsSolid | kind=design_pattern | label=state | domain=video | tier=minimal
package org.example.patterns;

interface VideoState {
    String handle(VideoContext ctx);
}

class VideoOnState implements VideoState {
    public String handle(VideoContext ctx) {
        ctx.setState(new VideoOffState());
        return "was-on-video";
    }
}

class VideoOffState implements VideoState {
    public String handle(VideoContext ctx) {
        ctx.setState(new VideoOnState());
        return "was-off-video";
    }
}

public class VideoContext {
    private VideoState state = new VideoOffState();
    public void setState(VideoState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
