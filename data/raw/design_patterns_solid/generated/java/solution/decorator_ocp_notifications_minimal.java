// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=notifications | tier=minimal
package org.example.patterns;

interface NotificationsComponent {
    String process(String input);
}

class NotificationsCore implements NotificationsComponent {
    public String process(String input) { return "notifications:" + input; }
}

public class NotificationsUpperDecorator implements NotificationsComponent {
    private final NotificationsComponent inner;
    public NotificationsUpperDecorator(NotificationsComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}
