// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=sensors | tier=logging
package org.example.patterns;

interface SensorsButton { String render(); }
interface SensorsDialog { String show(); }

class SensorsCloudButton implements SensorsButton {
    public String render() { return "cloud-btn-sensors"; }
}
class SensorsCloudDialog implements SensorsDialog {
    public String show() { return "cloud-dlg-sensors"; }
}
class SensorsLocalButton implements SensorsButton {
    public String render() { return "local-btn-sensors"; }
}
class SensorsLocalDialog implements SensorsDialog {
    public String show() { return "local-dlg-sensors"; }
}

interface SensorsUIFactory {
    SensorsButton createButton();
    SensorsDialog createDialog();
}

class SensorsCloudFactory implements SensorsUIFactory {
    public SensorsButton createButton() { return new SensorsCloudButton(); }
    public SensorsDialog createDialog() { return new SensorsCloudDialog(); }
}

class SensorsLocalFactory implements SensorsUIFactory {
    public SensorsButton createButton() { return new SensorsLocalButton(); }
    public SensorsDialog createDialog() { return new SensorsLocalDialog(); }
}

public class SensorsAbstractFactoryDemo {
    public static String run(SensorsUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
