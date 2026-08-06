// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=metrics | tier=logging
package org.example.patterns;

interface MetricsButton { String render(); }
interface MetricsDialog { String show(); }

class MetricsCloudButton implements MetricsButton {
    public String render() { return "cloud-btn-metrics"; }
}
class MetricsCloudDialog implements MetricsDialog {
    public String show() { return "cloud-dlg-metrics"; }
}
class MetricsLocalButton implements MetricsButton {
    public String render() { return "local-btn-metrics"; }
}
class MetricsLocalDialog implements MetricsDialog {
    public String show() { return "local-dlg-metrics"; }
}

interface MetricsUIFactory {
    MetricsButton createButton();
    MetricsDialog createDialog();
}

class MetricsCloudFactory implements MetricsUIFactory {
    public MetricsButton createButton() { return new MetricsCloudButton(); }
    public MetricsDialog createDialog() { return new MetricsCloudDialog(); }
}

class MetricsLocalFactory implements MetricsUIFactory {
    public MetricsButton createButton() { return new MetricsLocalButton(); }
    public MetricsDialog createDialog() { return new MetricsLocalDialog(); }
}

public class MetricsAbstractFactoryDemo {
    public static String run(MetricsUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
