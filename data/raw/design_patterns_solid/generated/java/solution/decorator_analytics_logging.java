// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=analytics | tier=logging
package org.example.patterns;

interface AnalyticsComponent {
    String process(String input);
}

class AnalyticsCore implements AnalyticsComponent {
    public String process(String input) { return "analytics:" + input; }
}

public class AnalyticsUpperDecorator implements AnalyticsComponent {
    private final AnalyticsComponent inner;
    public AnalyticsUpperDecorator(AnalyticsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
