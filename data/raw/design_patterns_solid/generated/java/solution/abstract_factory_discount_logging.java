// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=discount | tier=logging
package org.example.patterns;

interface DiscountButton { String render(); }
interface DiscountDialog { String show(); }

class DiscountCloudButton implements DiscountButton {
    public String render() { return "cloud-btn-discount"; }
}
class DiscountCloudDialog implements DiscountDialog {
    public String show() { return "cloud-dlg-discount"; }
}
class DiscountLocalButton implements DiscountButton {
    public String render() { return "local-btn-discount"; }
}
class DiscountLocalDialog implements DiscountDialog {
    public String show() { return "local-dlg-discount"; }
}

interface DiscountUIFactory {
    DiscountButton createButton();
    DiscountDialog createDialog();
}

class DiscountCloudFactory implements DiscountUIFactory {
    public DiscountButton createButton() { return new DiscountCloudButton(); }
    public DiscountDialog createDialog() { return new DiscountCloudDialog(); }
}

class DiscountLocalFactory implements DiscountUIFactory {
    public DiscountButton createButton() { return new DiscountLocalButton(); }
    public DiscountDialog createDialog() { return new DiscountLocalDialog(); }
}

public class DiscountAbstractFactoryDemo {
    public static String run(DiscountUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
