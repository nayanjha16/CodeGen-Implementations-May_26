// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=tax | tier=logging
package org.example.patterns;

interface TaxButton { String render(); }
interface TaxDialog { String show(); }

class TaxCloudButton implements TaxButton {
    public String render() { return "cloud-btn-tax"; }
}
class TaxCloudDialog implements TaxDialog {
    public String show() { return "cloud-dlg-tax"; }
}
class TaxLocalButton implements TaxButton {
    public String render() { return "local-btn-tax"; }
}
class TaxLocalDialog implements TaxDialog {
    public String show() { return "local-dlg-tax"; }
}

interface TaxUIFactory {
    TaxButton createButton();
    TaxDialog createDialog();
}

class TaxCloudFactory implements TaxUIFactory {
    public TaxButton createButton() { return new TaxCloudButton(); }
    public TaxDialog createDialog() { return new TaxCloudDialog(); }
}

class TaxLocalFactory implements TaxUIFactory {
    public TaxButton createButton() { return new TaxLocalButton(); }
    public TaxDialog createDialog() { return new TaxLocalDialog(); }
}

public class TaxAbstractFactoryDemo {
    public static String run(TaxUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
