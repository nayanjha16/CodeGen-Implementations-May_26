// DesignPatternsSolid | kind=design_pattern | label=state | domain=sensors | tier=errors
package org.example.patterns;

interface SensorsState {
    String handle(SensorsContext ctx);
}

class SensorsOnState implements SensorsState {
    public String handle(SensorsContext ctx) {
        ctx.setState(new SensorsOffState());
        return "was-on-sensors";
    }
}

class SensorsOffState implements SensorsState {
    public String handle(SensorsContext ctx) {
        ctx.setState(new SensorsOnState());
        return "was-off-sensors";
    }
}

public class SensorsContext {
    private SensorsState state = new SensorsOffState();
    public void setState(SensorsState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
