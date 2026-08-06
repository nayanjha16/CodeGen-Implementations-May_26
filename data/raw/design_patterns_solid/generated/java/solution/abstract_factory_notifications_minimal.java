// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=notifications | tier=minimal
package org.example.patterns;

interface NotificationsButton { String render(); }
interface NotificationsDialog { String show(); }

class NotificationsCloudButton implements NotificationsButton {
    public String render() { return "cloud-btn-notifications"; }
}
class NotificationsCloudDialog implements NotificationsDialog {
    public String show() { return "cloud-dlg-notifications"; }
}
class NotificationsLocalButton implements NotificationsButton {
    public String render() { return "local-btn-notifications"; }
}
class NotificationsLocalDialog implements NotificationsDialog {
    public String show() { return "local-dlg-notifications"; }
}

interface NotificationsUIFactory {
    NotificationsButton createButton();
    NotificationsDialog createDialog();
}

class NotificationsCloudFactory implements NotificationsUIFactory {
    public NotificationsButton createButton() { return new NotificationsCloudButton(); }
    public NotificationsDialog createDialog() { return new NotificationsCloudDialog(); }
}

class NotificationsLocalFactory implements NotificationsUIFactory {
    public NotificationsButton createButton() { return new NotificationsLocalButton(); }
    public NotificationsDialog createDialog() { return new NotificationsLocalDialog(); }
}

public class NotificationsAbstractFactoryDemo {
    public static String run(NotificationsUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
