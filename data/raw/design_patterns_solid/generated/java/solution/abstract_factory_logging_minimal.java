// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=logging | tier=minimal
package org.example.patterns;

interface LoggingButton { String render(); }
interface LoggingDialog { String show(); }

class LoggingCloudButton implements LoggingButton {
    public String render() { return "cloud-btn-logging"; }
}
class LoggingCloudDialog implements LoggingDialog {
    public String show() { return "cloud-dlg-logging"; }
}
class LoggingLocalButton implements LoggingButton {
    public String render() { return "local-btn-logging"; }
}
class LoggingLocalDialog implements LoggingDialog {
    public String show() { return "local-dlg-logging"; }
}

interface LoggingUIFactory {
    LoggingButton createButton();
    LoggingDialog createDialog();
}

class LoggingCloudFactory implements LoggingUIFactory {
    public LoggingButton createButton() { return new LoggingCloudButton(); }
    public LoggingDialog createDialog() { return new LoggingCloudDialog(); }
}

class LoggingLocalFactory implements LoggingUIFactory {
    public LoggingButton createButton() { return new LoggingLocalButton(); }
    public LoggingDialog createDialog() { return new LoggingLocalDialog(); }
}

public class LoggingAbstractFactoryDemo {
    public static String run(LoggingUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
