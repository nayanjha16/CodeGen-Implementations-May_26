// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=http | tier=logging
package org.example.patterns;

interface HttpButton { String render(); }
interface HttpDialog { String show(); }

class HttpCloudButton implements HttpButton {
    public String render() { return "cloud-btn-http"; }
}
class HttpCloudDialog implements HttpDialog {
    public String show() { return "cloud-dlg-http"; }
}
class HttpLocalButton implements HttpButton {
    public String render() { return "local-btn-http"; }
}
class HttpLocalDialog implements HttpDialog {
    public String show() { return "local-dlg-http"; }
}

interface HttpUIFactory {
    HttpButton createButton();
    HttpDialog createDialog();
}

class HttpCloudFactory implements HttpUIFactory {
    public HttpButton createButton() { return new HttpCloudButton(); }
    public HttpDialog createDialog() { return new HttpCloudDialog(); }
}

class HttpLocalFactory implements HttpUIFactory {
    public HttpButton createButton() { return new HttpLocalButton(); }
    public HttpDialog createDialog() { return new HttpLocalDialog(); }
}

public class HttpAbstractFactoryDemo {
    public static String run(HttpUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
