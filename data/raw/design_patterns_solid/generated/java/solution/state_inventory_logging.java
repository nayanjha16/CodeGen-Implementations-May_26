// DesignPatternsSolid | kind=design_pattern | label=state | domain=inventory | tier=logging
package org.example.patterns;

interface InventoryState {
    String handle(InventoryContext ctx);
}

class InventoryOnState implements InventoryState {
    public String handle(InventoryContext ctx) {
        ctx.setState(new InventoryOffState());
        return "was-on-inventory";
    }
}

class InventoryOffState implements InventoryState {
    public String handle(InventoryContext ctx) {
        ctx.setState(new InventoryOnState());
        return "was-off-inventory";
    }
}

public class InventoryContext {
    private InventoryState state = new InventoryOffState();
    public void setState(InventoryState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
