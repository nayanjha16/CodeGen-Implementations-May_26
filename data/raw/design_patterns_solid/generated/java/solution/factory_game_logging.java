// DesignPatternsSolid | kind=design_pattern | label=factory | domain=game | tier=logging
package org.example.patterns;

interface GameProduct {
    String operate();
}

class GameBasicProduct implements GameProduct {
    public String operate() { return "basic-game"; }
}

class GamePremiumProduct implements GameProduct {
    public String operate() { return "premium-game"; }
}

public class GameFactory {
    public GameProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new GamePremiumProduct();
        return new GameBasicProduct();
    }
}
