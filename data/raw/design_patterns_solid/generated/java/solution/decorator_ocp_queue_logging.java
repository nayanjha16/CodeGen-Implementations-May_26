// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=queue | tier=logging
package org.example.patterns;

interface QueueComponent {
    String process(String input);
}

class QueueCore implements QueueComponent {
    public String process(String input) { return "queue:" + input; }
}

public class QueueUpperDecorator implements QueueComponent {
    private final QueueComponent inner;
    public QueueUpperDecorator(QueueComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
