// DesignPatternsSolid | kind=design_pattern | label=template method | domain=map | tier=logging
package org.example.patterns;

public abstract class MapTemplate {
    public final String run(String input) {
        String prepared = prepare(input);
        String processed = process(prepared);
        return finish(processed);
    }
    protected String prepare(String input) { return input.trim(); }
    protected abstract String process(String input);
    protected String finish(String input) { return "map|" + input; }
}

class MapUpperTemplate extends MapTemplate {
    protected String process(String input) { return input.toUpperCase(); }
}
