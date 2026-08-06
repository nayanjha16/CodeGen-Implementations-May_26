// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=map | tier=minimal
package org.example.patterns;

interface MapService {
    String load(String id);
}

class MapRealService implements MapService {
    public String load(String id) { return "real-map:" + id; }
}

public class MapProxy implements MapService {
    private MapRealService real;
    private final boolean allowed;
    public MapProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new MapRealService();
        return real.load(id);
    }
}
