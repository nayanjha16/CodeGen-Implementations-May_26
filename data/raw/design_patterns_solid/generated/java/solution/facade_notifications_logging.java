// DesignPatternsSolid | kind=design_pattern | label=facade | domain=notifications | tier=logging
package org.example.patterns;

class NotificationsValidator {
    public boolean ok(String v) { return v != null && !v.isEmpty(); }
}
class NotificationsWriter {
    public String write(String v) { return "wrote-notifications:" + v; }
}
public class NotificationsFacade {
    private final NotificationsValidator validator = new NotificationsValidator();
    private final NotificationsWriter writer = new NotificationsWriter();
    public String submit(String value) {
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }
}
