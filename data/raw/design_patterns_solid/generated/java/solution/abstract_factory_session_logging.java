// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=session | tier=logging
package org.example.patterns;

interface SessionButton { String render(); }
interface SessionDialog { String show(); }

class SessionCloudButton implements SessionButton {
    public String render() { return "cloud-btn-session"; }
}
class SessionCloudDialog implements SessionDialog {
    public String show() { return "cloud-dlg-session"; }
}
class SessionLocalButton implements SessionButton {
    public String render() { return "local-btn-session"; }
}
class SessionLocalDialog implements SessionDialog {
    public String show() { return "local-dlg-session"; }
}

interface SessionUIFactory {
    SessionButton createButton();
    SessionDialog createDialog();
}

class SessionCloudFactory implements SessionUIFactory {
    public SessionButton createButton() { return new SessionCloudButton(); }
    public SessionDialog createDialog() { return new SessionCloudDialog(); }
}

class SessionLocalFactory implements SessionUIFactory {
    public SessionButton createButton() { return new SessionLocalButton(); }
    public SessionDialog createDialog() { return new SessionLocalDialog(); }
}

public class SessionAbstractFactoryDemo {
    public static String run(SessionUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
