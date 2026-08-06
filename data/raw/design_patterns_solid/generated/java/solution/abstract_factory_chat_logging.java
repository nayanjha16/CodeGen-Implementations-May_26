// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=chat | tier=logging
package org.example.patterns;

interface ChatButton { String render(); }
interface ChatDialog { String show(); }

class ChatCloudButton implements ChatButton {
    public String render() { return "cloud-btn-chat"; }
}
class ChatCloudDialog implements ChatDialog {
    public String show() { return "cloud-dlg-chat"; }
}
class ChatLocalButton implements ChatButton {
    public String render() { return "local-btn-chat"; }
}
class ChatLocalDialog implements ChatDialog {
    public String show() { return "local-dlg-chat"; }
}

interface ChatUIFactory {
    ChatButton createButton();
    ChatDialog createDialog();
}

class ChatCloudFactory implements ChatUIFactory {
    public ChatButton createButton() { return new ChatCloudButton(); }
    public ChatDialog createDialog() { return new ChatCloudDialog(); }
}

class ChatLocalFactory implements ChatUIFactory {
    public ChatButton createButton() { return new ChatLocalButton(); }
    public ChatDialog createDialog() { return new ChatLocalDialog(); }
}

public class ChatAbstractFactoryDemo {
    public static String run(ChatUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
