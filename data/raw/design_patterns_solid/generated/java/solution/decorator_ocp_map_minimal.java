// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=map | tier=minimal
package org.example.patterns;

interface MapComponent {
    String process(String input);
}

class MapCore implements MapComponent {
    public String process(String input) { return "map:" + input; }
}

public class MapUpperDecorator implements MapComponent {
    private final MapComponent inner;
    public MapUpperDecorator(MapComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
