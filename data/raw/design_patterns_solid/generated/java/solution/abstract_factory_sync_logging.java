// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=sync | tier=logging
package org.example.patterns;

interface SyncButton { String render(); }
interface SyncDialog { String show(); }

class SyncCloudButton implements SyncButton {
    public String render() { return "cloud-btn-sync"; }
}
class SyncCloudDialog implements SyncDialog {
    public String show() { return "cloud-dlg-sync"; }
}
class SyncLocalButton implements SyncButton {
    public String render() { return "local-btn-sync"; }
}
class SyncLocalDialog implements SyncDialog {
    public String show() { return "local-dlg-sync"; }
}

interface SyncUIFactory {
    SyncButton createButton();
    SyncDialog createDialog();
}

class SyncCloudFactory implements SyncUIFactory {
    public SyncButton createButton() { return new SyncCloudButton(); }
    public SyncDialog createDialog() { return new SyncCloudDialog(); }
}

class SyncLocalFactory implements SyncUIFactory {
    public SyncButton createButton() { return new SyncLocalButton(); }
    public SyncDialog createDialog() { return new SyncLocalDialog(); }
}

public class SyncAbstractFactoryDemo {
    public static String run(SyncUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
