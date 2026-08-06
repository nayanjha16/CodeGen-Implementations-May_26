// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=notifications | tier=logging
package org.example.patterns;

interface NotificationsVisitor {
    String visitLeaf(NotificationsLeaf leaf);
}

interface NotificationsElement {
    String accept(NotificationsVisitor v);
}

class NotificationsLeaf implements NotificationsElement {
    final String name;
    public NotificationsLeaf(String name) { this.name = name; }
    public String accept(NotificationsVisitor v) { return v.visitLeaf(this); }
}

public class NotificationsPrintVisitor implements NotificationsVisitor {
    public String visitLeaf(NotificationsLeaf leaf) { return "notifications:" + leaf.name; }
}
