// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=metrics | tier=logging
package org.example.patterns;

interface MetricsComponent {
    String process(String input);
}

class MetricsCore implements MetricsComponent {
    public String process(String input) { return "metrics:" + input; }
}

public class MetricsUpperDecorator implements MetricsComponent {
    private final MetricsComponent inner;
    public MetricsUpperDecorator(MetricsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
