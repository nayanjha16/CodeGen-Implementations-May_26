// DesignPatternsSolid | kind=design_pattern | label=state | domain=map | tier=errors
package org.example.patterns;

interface MapState {
    String handle(MapContext ctx);
}

class MapOnState implements MapState {
    public String handle(MapContext ctx) {
        ctx.setState(new MapOffState());
        return "was-on-map";
    }
}

class MapOffState implements MapState {
    public String handle(MapContext ctx) {
        ctx.setState(new MapOnState());
        return "was-off-map";
    }
}

public class MapContext {
    private MapState state = new MapOffState();
    public void setState(MapState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
