// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=widgets | tier=errors
package org.example.patterns;

interface WidgetsComponent {
    String process(String input);
}

class WidgetsCore implements WidgetsComponent {
    public String process(String input) { return "widgets:" + input; }
}

public class WidgetsUpperDecorator implements WidgetsComponent {
    private final WidgetsComponent inner;
    public WidgetsUpperDecorator(WidgetsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
