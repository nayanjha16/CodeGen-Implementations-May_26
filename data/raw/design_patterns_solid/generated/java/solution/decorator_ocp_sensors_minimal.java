// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=sensors | tier=minimal
package org.example.patterns;

interface SensorsComponent {
    String process(String input);
}

class SensorsCore implements SensorsComponent {
    public String process(String input) { return "sensors:" + input; }
}

public class SensorsUpperDecorator implements SensorsComponent {
    private final SensorsComponent inner;
    public SensorsUpperDecorator(SensorsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
