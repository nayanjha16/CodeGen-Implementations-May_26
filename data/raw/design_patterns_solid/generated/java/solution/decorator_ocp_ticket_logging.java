// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=ticket | tier=logging
package org.example.patterns;

interface TicketComponent {
    String process(String input);
}

class TicketCore implements TicketComponent {
    public String process(String input) { return "ticket:" + input; }
}

public class TicketUpperDecorator implements TicketComponent {
    private final TicketComponent inner;
    public TicketUpperDecorator(TicketComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
