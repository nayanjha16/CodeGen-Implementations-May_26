// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=backup | tier=minimal
package org.example.patterns;

interface BackupButton { String render(); }
interface BackupDialog { String show(); }

class BackupCloudButton implements BackupButton {
    public String render() { return "cloud-btn-backup"; }
}
class BackupCloudDialog implements BackupDialog {
    public String show() { return "cloud-dlg-backup"; }
}
class BackupLocalButton implements BackupButton {
    public String render() { return "local-btn-backup"; }
}
class BackupLocalDialog implements BackupDialog {
    public String show() { return "local-dlg-backup"; }
}

interface BackupUIFactory {
    BackupButton createButton();
    BackupDialog createDialog();
}

class BackupCloudFactory implements BackupUIFactory {
    public BackupButton createButton() { return new BackupCloudButton(); }
    public BackupDialog createDialog() { return new BackupCloudDialog(); }
}

class BackupLocalFactory implements BackupUIFactory {
    public BackupButton createButton() { return new BackupLocalButton(); }
    public BackupDialog createDialog() { return new BackupLocalDialog(); }
}

public class BackupAbstractFactoryDemo {
    public static String run(BackupUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
