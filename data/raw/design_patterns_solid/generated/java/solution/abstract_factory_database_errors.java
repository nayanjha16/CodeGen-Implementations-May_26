// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=database | tier=errors
package org.example.patterns;

interface DatabaseButton { String render(); }
interface DatabaseDialog { String show(); }

class DatabaseCloudButton implements DatabaseButton {
    public String render() { return "cloud-btn-database"; }
}
class DatabaseCloudDialog implements DatabaseDialog {
    public String show() { return "cloud-dlg-database"; }
}
class DatabaseLocalButton implements DatabaseButton {
    public String render() { return "local-btn-database"; }
}
class DatabaseLocalDialog implements DatabaseDialog {
    public String show() { return "local-dlg-database"; }
}

interface DatabaseUIFactory {
    DatabaseButton createButton();
    DatabaseDialog createDialog();
}

class DatabaseCloudFactory implements DatabaseUIFactory {
    public DatabaseButton createButton() { return new DatabaseCloudButton(); }
    public DatabaseDialog createDialog() { return new DatabaseCloudDialog(); }
}

class DatabaseLocalFactory implements DatabaseUIFactory {
    public DatabaseButton createButton() { return new DatabaseLocalButton(); }
    public DatabaseDialog createDialog() { return new DatabaseLocalDialog(); }
}

public class DatabaseAbstractFactoryDemo {
    public static String run(DatabaseUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
