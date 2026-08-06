// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=plugin | tier=minimal
package org.example.patterns;

interface PluginButton { String render(); }
interface PluginDialog { String show(); }

class PluginCloudButton implements PluginButton {
    public String render() { return "cloud-btn-plugin"; }
}
class PluginCloudDialog implements PluginDialog {
    public String show() { return "cloud-dlg-plugin"; }
}
class PluginLocalButton implements PluginButton {
    public String render() { return "local-btn-plugin"; }
}
class PluginLocalDialog implements PluginDialog {
    public String show() { return "local-dlg-plugin"; }
}

interface PluginUIFactory {
    PluginButton createButton();
    PluginDialog createDialog();
}

class PluginCloudFactory implements PluginUIFactory {
    public PluginButton createButton() { return new PluginCloudButton(); }
    public PluginDialog createDialog() { return new PluginCloudDialog(); }
}

class PluginLocalFactory implements PluginUIFactory {
    public PluginButton createButton() { return new PluginLocalButton(); }
    public PluginDialog createDialog() { return new PluginLocalDialog(); }
}

public class PluginAbstractFactoryDemo {
    public static String run(PluginUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
