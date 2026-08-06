// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=game | tier=logging
package org.example.patterns;

interface GameService {
    String load(String id);
}

class GameRealService implements GameService {
    public String load(String id) { return "real-game:" + id; }
}

public class GameProxy implements GameService {
    private GameRealService real;
    private final boolean allowed;
    public GameProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new GameRealService();
        return real.load(id);
    }
}
