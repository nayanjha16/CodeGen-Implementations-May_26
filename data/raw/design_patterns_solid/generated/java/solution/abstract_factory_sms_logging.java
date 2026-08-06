// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=sms | tier=logging
package org.example.patterns;

interface SmsButton { String render(); }
interface SmsDialog { String show(); }

class SmsCloudButton implements SmsButton {
    public String render() { return "cloud-btn-sms"; }
}
class SmsCloudDialog implements SmsDialog {
    public String show() { return "cloud-dlg-sms"; }
}
class SmsLocalButton implements SmsButton {
    public String render() { return "local-btn-sms"; }
}
class SmsLocalDialog implements SmsDialog {
    public String show() { return "local-dlg-sms"; }
}

interface SmsUIFactory {
    SmsButton createButton();
    SmsDialog createDialog();
}

class SmsCloudFactory implements SmsUIFactory {
    public SmsButton createButton() { return new SmsCloudButton(); }
    public SmsDialog createDialog() { return new SmsCloudDialog(); }
}

class SmsLocalFactory implements SmsUIFactory {
    public SmsButton createButton() { return new SmsLocalButton(); }
    public SmsDialog createDialog() { return new SmsLocalDialog(); }
}

public class SmsAbstractFactoryDemo {
    public static String run(SmsUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
