// DesignPatternsSolid | kind=design_pattern | label=state | domain=feed | tier=logging
package org.example.patterns;

interface FeedState {
    String handle(FeedContext ctx);
}

class FeedOnState implements FeedState {
    public String handle(FeedContext ctx) {
        ctx.setState(new FeedOffState());
        return "was-on-feed";
    }
}

class FeedOffState implements FeedState {
    public String handle(FeedContext ctx) {
        ctx.setState(new FeedOnState());
        return "was-off-feed";
    }
}

public class FeedContext {
    private FeedState state = new FeedOffState();
    public void setState(FeedState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
