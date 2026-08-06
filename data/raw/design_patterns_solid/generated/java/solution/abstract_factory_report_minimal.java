// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=report | tier=minimal
package org.example.patterns;

interface ReportButton { String render(); }
interface ReportDialog { String show(); }

class ReportCloudButton implements ReportButton {
    public String render() { return "cloud-btn-report"; }
}
class ReportCloudDialog implements ReportDialog {
    public String show() { return "cloud-dlg-report"; }
}
class ReportLocalButton implements ReportButton {
    public String render() { return "local-btn-report"; }
}
class ReportLocalDialog implements ReportDialog {
    public String show() { return "local-dlg-report"; }
}

interface ReportUIFactory {
    ReportButton createButton();
    ReportDialog createDialog();
}

class ReportCloudFactory implements ReportUIFactory {
    public ReportButton createButton() { return new ReportCloudButton(); }
    public ReportDialog createDialog() { return new ReportCloudDialog(); }
}

class ReportLocalFactory implements ReportUIFactory {
    public ReportButton createButton() { return new ReportLocalButton(); }
    public ReportDialog createDialog() { return new ReportLocalDialog(); }
}

public class ReportAbstractFactoryDemo {
    public static String run(ReportUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
