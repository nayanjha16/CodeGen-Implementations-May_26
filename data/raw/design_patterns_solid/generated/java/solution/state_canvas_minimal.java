// DesignPatternsSolid | kind=design_pattern | label=state | domain=canvas | tier=minimal
package org.example.patterns;

interface CanvasState {
    String handle(CanvasContext ctx);
}

class CanvasOnState implements CanvasState {
    public String handle(CanvasContext ctx) {
        ctx.setState(new CanvasOffState());
        return "was-on-canvas";
    }
}

class CanvasOffState implements CanvasState {
    public String handle(CanvasContext ctx) {
        ctx.setState(new CanvasOnState());
        return "was-off-canvas";
    }
}

public class CanvasContext {
    private CanvasState state = new CanvasOffState();
    public void setState(CanvasState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
