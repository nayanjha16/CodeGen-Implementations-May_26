// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=payments | tier=logging
package org.example.patterns;

interface PaymentsButton { String render(); }
interface PaymentsDialog { String show(); }

class PaymentsCloudButton implements PaymentsButton {
    public String render() { return "cloud-btn-payments"; }
}
class PaymentsCloudDialog implements PaymentsDialog {
    public String show() { return "cloud-dlg-payments"; }
}
class PaymentsLocalButton implements PaymentsButton {
    public String render() { return "local-btn-payments"; }
}
class PaymentsLocalDialog implements PaymentsDialog {
    public String show() { return "local-dlg-payments"; }
}

interface PaymentsUIFactory {
    PaymentsButton createButton();
    PaymentsDialog createDialog();
}

class PaymentsCloudFactory implements PaymentsUIFactory {
    public PaymentsButton createButton() { return new PaymentsCloudButton(); }
    public PaymentsDialog createDialog() { return new PaymentsCloudDialog(); }
}

class PaymentsLocalFactory implements PaymentsUIFactory {
    public PaymentsButton createButton() { return new PaymentsLocalButton(); }
    public PaymentsDialog createDialog() { return new PaymentsLocalDialog(); }
}

public class PaymentsAbstractFactoryDemo {
    public static String run(PaymentsUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
