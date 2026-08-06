// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=cart | tier=minimal
package org.example.patterns;

interface CartButton { String render(); }
interface CartDialog { String show(); }

class CartCloudButton implements CartButton {
    public String render() { return "cloud-btn-cart"; }
}
class CartCloudDialog implements CartDialog {
    public String show() { return "cloud-dlg-cart"; }
}
class CartLocalButton implements CartButton {
    public String render() { return "local-btn-cart"; }
}
class CartLocalDialog implements CartDialog {
    public String show() { return "local-dlg-cart"; }
}

interface CartUIFactory {
    CartButton createButton();
    CartDialog createDialog();
}

class CartCloudFactory implements CartUIFactory {
    public CartButton createButton() { return new CartCloudButton(); }
    public CartDialog createDialog() { return new CartCloudDialog(); }
}

class CartLocalFactory implements CartUIFactory {
    public CartButton createButton() { return new CartLocalButton(); }
    public CartDialog createDialog() { return new CartLocalDialog(); }
}

public class CartAbstractFactoryDemo {
    public static String run(CartUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
