// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=storage | tier=minimal
package org.example.patterns;

interface StorageButton { String render(); }
interface StorageDialog { String show(); }

class StorageCloudButton implements StorageButton {
    public String render() { return "cloud-btn-storage"; }
}
class StorageCloudDialog implements StorageDialog {
    public String show() { return "cloud-dlg-storage"; }
}
class StorageLocalButton implements StorageButton {
    public String render() { return "local-btn-storage"; }
}
class StorageLocalDialog implements StorageDialog {
    public String show() { return "local-dlg-storage"; }
}

interface StorageUIFactory {
    StorageButton createButton();
    StorageDialog createDialog();
}

class StorageCloudFactory implements StorageUIFactory {
    public StorageButton createButton() { return new StorageCloudButton(); }
    public StorageDialog createDialog() { return new StorageCloudDialog(); }
}

class StorageLocalFactory implements StorageUIFactory {
    public StorageButton createButton() { return new StorageLocalButton(); }
    public StorageDialog createDialog() { return new StorageLocalDialog(); }
}

public class StorageAbstractFactoryDemo {
    public static String run(StorageUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
