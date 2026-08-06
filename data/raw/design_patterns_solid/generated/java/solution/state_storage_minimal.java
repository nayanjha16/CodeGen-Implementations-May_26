// DesignPatternsSolid | kind=design_pattern | label=state | domain=storage | tier=minimal
package org.example.patterns;

interface StorageState {
    String handle(StorageContext ctx);
}

class StorageOnState implements StorageState {
    public String handle(StorageContext ctx) {
        ctx.setState(new StorageOffState());
        return "was-on-storage";
    }
}

class StorageOffState implements StorageState {
    public String handle(StorageContext ctx) {
        ctx.setState(new StorageOnState());
        return "was-off-storage";
    }
}

public class StorageContext {
    private StorageState state = new StorageOffState();
    public void setState(StorageState state) { this.state = state; }
    public String request() { return state.handle(this); }
}
