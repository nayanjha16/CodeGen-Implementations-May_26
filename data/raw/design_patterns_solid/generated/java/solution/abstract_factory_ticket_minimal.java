// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=ticket | tier=minimal
package org.example.patterns;

interface TicketButton { String render(); }
interface TicketDialog { String show(); }

class TicketCloudButton implements TicketButton {
    public String render() { return "cloud-btn-ticket"; }
}
class TicketCloudDialog implements TicketDialog {
    public String show() { return "cloud-dlg-ticket"; }
}
class TicketLocalButton implements TicketButton {
    public String render() { return "local-btn-ticket"; }
}
class TicketLocalDialog implements TicketDialog {
    public String show() { return "local-dlg-ticket"; }
}

interface TicketUIFactory {
    TicketButton createButton();
    TicketDialog createDialog();
}

class TicketCloudFactory implements TicketUIFactory {
    public TicketButton createButton() { return new TicketCloudButton(); }
    public TicketDialog createDialog() { return new TicketCloudDialog(); }
}

class TicketLocalFactory implements TicketUIFactory {
    public TicketButton createButton() { return new TicketLocalButton(); }
    public TicketDialog createDialog() { return new TicketLocalDialog(); }
}

public class TicketAbstractFactoryDemo {
    public static String run(TicketUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
