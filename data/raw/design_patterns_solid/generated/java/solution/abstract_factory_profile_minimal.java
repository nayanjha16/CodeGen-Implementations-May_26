// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=profile | tier=minimal
package org.example.patterns;

interface ProfileButton { String render(); }
interface ProfileDialog { String show(); }

class ProfileCloudButton implements ProfileButton {
    public String render() { return "cloud-btn-profile"; }
}
class ProfileCloudDialog implements ProfileDialog {
    public String show() { return "cloud-dlg-profile"; }
}
class ProfileLocalButton implements ProfileButton {
    public String render() { return "local-btn-profile"; }
}
class ProfileLocalDialog implements ProfileDialog {
    public String show() { return "local-dlg-profile"; }
}

interface ProfileUIFactory {
    ProfileButton createButton();
    ProfileDialog createDialog();
}

class ProfileCloudFactory implements ProfileUIFactory {
    public ProfileButton createButton() { return new ProfileCloudButton(); }
    public ProfileDialog createDialog() { return new ProfileCloudDialog(); }
}

class ProfileLocalFactory implements ProfileUIFactory {
    public ProfileButton createButton() { return new ProfileLocalButton(); }
    public ProfileDialog createDialog() { return new ProfileLocalDialog(); }
}

public class ProfileAbstractFactoryDemo {
    public static String run(ProfileUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
