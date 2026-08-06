// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=game | tier=logging
package org.example.patterns;

interface GameImpl {
    String write(String msg);
}

class GameFileImpl implements GameImpl {
    public String write(String msg) { return "file:game:" + msg; }
}

class GameMemoryImpl implements GameImpl {
    public String write(String msg) { return "mem:game:" + msg; }
}

public abstract class GameBridge {
    protected final GameImpl impl;
    protected GameBridge(GameImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class GameAlertBridge extends GameBridge {
    public GameAlertBridge(GameImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
