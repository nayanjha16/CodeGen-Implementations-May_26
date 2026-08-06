// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=config | tier=errors
package org.example.patterns;

interface ConfigComponent {
    String process(String input);
}

class ConfigCore implements ConfigComponent {
    public String process(String input) { return "config:" + input; }
}

public class ConfigUpperDecorator implements ConfigComponent {
    private final ConfigComponent inner;
    public ConfigUpperDecorator(ConfigComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
