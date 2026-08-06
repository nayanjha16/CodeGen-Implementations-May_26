// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=scheduling | tier=minimal
package org.example.patterns;

interface SchedulingComponent {
    String process(String input);
}

class SchedulingCore implements SchedulingComponent {
    public String process(String input) { return "scheduling:" + input; }
}

public class SchedulingUpperDecorator implements SchedulingComponent {
    private final SchedulingComponent inner;
    public SchedulingUpperDecorator(SchedulingComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
