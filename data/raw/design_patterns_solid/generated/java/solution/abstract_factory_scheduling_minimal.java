// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=scheduling | tier=minimal
package org.example.patterns;

interface SchedulingButton { String render(); }
interface SchedulingDialog { String show(); }

class SchedulingCloudButton implements SchedulingButton {
    public String render() { return "cloud-btn-scheduling"; }
}
class SchedulingCloudDialog implements SchedulingDialog {
    public String show() { return "cloud-dlg-scheduling"; }
}
class SchedulingLocalButton implements SchedulingButton {
    public String render() { return "local-btn-scheduling"; }
}
class SchedulingLocalDialog implements SchedulingDialog {
    public String show() { return "local-dlg-scheduling"; }
}

interface SchedulingUIFactory {
    SchedulingButton createButton();
    SchedulingDialog createDialog();
}

class SchedulingCloudFactory implements SchedulingUIFactory {
    public SchedulingButton createButton() { return new SchedulingCloudButton(); }
    public SchedulingDialog createDialog() { return new SchedulingCloudDialog(); }
}

class SchedulingLocalFactory implements SchedulingUIFactory {
    public SchedulingButton createButton() { return new SchedulingLocalButton(); }
    public SchedulingDialog createDialog() { return new SchedulingLocalDialog(); }
}

public class SchedulingAbstractFactoryDemo {
    public static String run(SchedulingUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
