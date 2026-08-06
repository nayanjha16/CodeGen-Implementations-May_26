// DesignPatternsSolid | kind=design_pattern | label=state | domain=review | tier=logging
package org.example.patterns;

interface ReviewState {
    String handle(ReviewContext ctx);
}

class ReviewOnState implements ReviewState {
    public String handle(ReviewContext ctx) {
        ctx.setState(new ReviewOffState());
        return "was-on-review";
    }
}

class ReviewOffState implements ReviewState {
    public String handle(ReviewContext ctx) {
        ctx.setState(new ReviewOnState());
        return "was-off-review";
    }
}

public class ReviewContext {
    private ReviewState state = new ReviewOffState();
    public void setState(ReviewState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
