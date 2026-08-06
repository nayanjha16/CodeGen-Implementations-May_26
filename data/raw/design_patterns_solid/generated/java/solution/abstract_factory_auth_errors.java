// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=auth | tier=errors
package org.example.patterns;

interface AuthButton { String render(); }
interface AuthDialog { String show(); }

class AuthCloudButton implements AuthButton {
    public String render() { return "cloud-btn-auth"; }
}
class AuthCloudDialog implements AuthDialog {
    public String show() { return "cloud-dlg-auth"; }
}
class AuthLocalButton implements AuthButton {
    public String render() { return "local-btn-auth"; }
}
class AuthLocalDialog implements AuthDialog {
    public String show() { return "local-dlg-auth"; }
}

interface AuthUIFactory {
    AuthButton createButton();
    AuthDialog createDialog();
}

class AuthCloudFactory implements AuthUIFactory {
    public AuthButton createButton() { return new AuthCloudButton(); }
    public AuthDialog createDialog() { return new AuthCloudDialog(); }
}

class AuthLocalFactory implements AuthUIFactory {
    public AuthButton createButton() { return new AuthLocalButton(); }
    public AuthDialog createDialog() { return new AuthLocalDialog(); }
}

public class AuthAbstractFactoryDemo {
    public static String run(AuthUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
