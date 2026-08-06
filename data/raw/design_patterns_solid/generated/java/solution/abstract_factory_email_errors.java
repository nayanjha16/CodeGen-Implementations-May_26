// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=email | tier=errors
package org.example.patterns;

interface EmailButton { String render(); }
interface EmailDialog { String show(); }

class EmailCloudButton implements EmailButton {
    public String render() { return "cloud-btn-email"; }
}
class EmailCloudDialog implements EmailDialog {
    public String show() { return "cloud-dlg-email"; }
}
class EmailLocalButton implements EmailButton {
    public String render() { return "local-btn-email"; }
}
class EmailLocalDialog implements EmailDialog {
    public String show() { return "local-dlg-email"; }
}

interface EmailUIFactory {
    EmailButton createButton();
    EmailDialog createDialog();
}

class EmailCloudFactory implements EmailUIFactory {
    public EmailButton createButton() { return new EmailCloudButton(); }
    public EmailDialog createDialog() { return new EmailCloudDialog(); }
}

class EmailLocalFactory implements EmailUIFactory {
    public EmailButton createButton() { return new EmailLocalButton(); }
    public EmailDialog createDialog() { return new EmailLocalDialog(); }
}

public class EmailAbstractFactoryDemo {
    public static String run(EmailUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
