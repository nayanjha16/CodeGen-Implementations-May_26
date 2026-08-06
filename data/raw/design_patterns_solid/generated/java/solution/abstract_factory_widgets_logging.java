// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=widgets | tier=logging
package org.example.patterns;

interface WidgetsButton { String render(); }
interface WidgetsDialog { String show(); }

class WidgetsCloudButton implements WidgetsButton {
    public String render() { return "cloud-btn-widgets"; }
}
class WidgetsCloudDialog implements WidgetsDialog {
    public String show() { return "cloud-dlg-widgets"; }
}
class WidgetsLocalButton implements WidgetsButton {
    public String render() { return "local-btn-widgets"; }
}
class WidgetsLocalDialog implements WidgetsDialog {
    public String show() { return "local-dlg-widgets"; }
}

interface WidgetsUIFactory {
    WidgetsButton createButton();
    WidgetsDialog createDialog();
}

class WidgetsCloudFactory implements WidgetsUIFactory {
    public WidgetsButton createButton() { return new WidgetsCloudButton(); }
    public WidgetsDialog createDialog() { return new WidgetsCloudDialog(); }
}

class WidgetsLocalFactory implements WidgetsUIFactory {
    public WidgetsButton createButton() { return new WidgetsLocalButton(); }
    public WidgetsDialog createDialog() { return new WidgetsLocalDialog(); }
}

public class WidgetsAbstractFactoryDemo {
    public static String run(WidgetsUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
