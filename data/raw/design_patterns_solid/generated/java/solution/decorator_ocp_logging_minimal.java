// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=logging | tier=minimal
package org.example.patterns;

interface LoggingComponent {
    String process(String input);
}

class LoggingCore implements LoggingComponent {
    public String process(String input) { return "logging:" + input; }
}

public class LoggingUpperDecorator implements LoggingComponent {
    private final LoggingComponent inner;
    public LoggingUpperDecorator(LoggingComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
