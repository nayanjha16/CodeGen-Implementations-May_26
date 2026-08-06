// DesignPatternsSolid | kind=design_pattern | label=decorator | domain=session | tier=minimal
package org.example.patterns;

interface SessionComponent {
    String process(String input);
}

class SessionCore implements SessionComponent {
    public String process(String input) { return "session:" + input; }
}

public class SessionUpperDecorator implements SessionComponent {
    private final SessionComponent inner;
    public SessionUpperDecorator(SessionComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
