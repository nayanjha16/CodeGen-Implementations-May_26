// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=cache | tier=logging
package org.example.patterns;

interface CacheButton { String render(); }
interface CacheDialog { String show(); }

class CacheCloudButton implements CacheButton {
    public String render() { return "cloud-btn-cache"; }
}
class CacheCloudDialog implements CacheDialog {
    public String show() { return "cloud-dlg-cache"; }
}
class CacheLocalButton implements CacheButton {
    public String render() { return "local-btn-cache"; }
}
class CacheLocalDialog implements CacheDialog {
    public String show() { return "local-dlg-cache"; }
}

interface CacheUIFactory {
    CacheButton createButton();
    CacheDialog createDialog();
}

class CacheCloudFactory implements CacheUIFactory {
    public CacheButton createButton() { return new CacheCloudButton(); }
    public CacheDialog createDialog() { return new CacheCloudDialog(); }
}

class CacheLocalFactory implements CacheUIFactory {
    public CacheButton createButton() { return new CacheLocalButton(); }
    public CacheDialog createDialog() { return new CacheLocalDialog(); }
}

public class CacheAbstractFactoryDemo {
    public static String run(CacheUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
