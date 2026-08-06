// DesignPatternsSolid | kind=design_pattern | label=template method | domain=config | tier=errors
package org.example.patterns;

public abstract class ConfigTemplate {
    public final String run(String input) {
        String prepared = prepare(input);
        String processed = process(prepared);
        return finish(processed);
    }
    protected String prepare(String input) { return input.trim(); }
    protected abstract String process(String input);
    protected String finish(String input) { return "config|" + input; }
}

class ConfigUpperTemplate extends ConfigTemplate {
    protected String process(String input) { return input.toUpperCase(); }
}
