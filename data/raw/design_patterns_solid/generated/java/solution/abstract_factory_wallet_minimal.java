// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletButton { String render(); }
interface WalletDialog { String show(); }

class WalletCloudButton implements WalletButton {
    public String render() { return "cloud-btn-wallet"; }
}
class WalletCloudDialog implements WalletDialog {
    public String show() { return "cloud-dlg-wallet"; }
}
class WalletLocalButton implements WalletButton {
    public String render() { return "local-btn-wallet"; }
}
class WalletLocalDialog implements WalletDialog {
    public String show() { return "local-dlg-wallet"; }
}

interface WalletUIFactory {
    WalletButton createButton();
    WalletDialog createDialog();
}

class WalletCloudFactory implements WalletUIFactory {
    public WalletButton createButton() { return new WalletCloudButton(); }
    public WalletDialog createDialog() { return new WalletCloudDialog(); }
}

class WalletLocalFactory implements WalletUIFactory {
    public WalletButton createButton() { return new WalletLocalButton(); }
    public WalletDialog createDialog() { return new WalletLocalDialog(); }
}

public class WalletAbstractFactoryDemo {
    public static String run(WalletUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
