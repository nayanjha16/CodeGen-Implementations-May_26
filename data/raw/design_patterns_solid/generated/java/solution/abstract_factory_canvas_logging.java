// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=canvas | tier=logging
package org.example.patterns;

interface CanvasButton { String render(); }
interface CanvasDialog { String show(); }

class CanvasCloudButton implements CanvasButton {
    public String render() { return "cloud-btn-canvas"; }
}
class CanvasCloudDialog implements CanvasDialog {
    public String show() { return "cloud-dlg-canvas"; }
}
class CanvasLocalButton implements CanvasButton {
    public String render() { return "local-btn-canvas"; }
}
class CanvasLocalDialog implements CanvasDialog {
    public String show() { return "local-dlg-canvas"; }
}

interface CanvasUIFactory {
    CanvasButton createButton();
    CanvasDialog createDialog();
}

class CanvasCloudFactory implements CanvasUIFactory {
    public CanvasButton createButton() { return new CanvasCloudButton(); }
    public CanvasDialog createDialog() { return new CanvasCloudDialog(); }
}

class CanvasLocalFactory implements CanvasUIFactory {
    public CanvasButton createButton() { return new CanvasLocalButton(); }
    public CanvasDialog createDialog() { return new CanvasLocalDialog(); }
}

public class CanvasAbstractFactoryDemo {
    public static String run(CanvasUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
