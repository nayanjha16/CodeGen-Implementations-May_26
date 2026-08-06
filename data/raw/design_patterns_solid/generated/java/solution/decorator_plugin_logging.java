// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=plugin | tier=logging
package org.example.patterns;

interface PluginComponent {
    String process(String input);
}

class PluginCore implements PluginComponent {
    public String process(String input) { return "plugin:" + input; }
}

public class PluginUpperDecorator implements PluginComponent {
    private final PluginComponent inner;
    public PluginUpperDecorator(PluginComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
