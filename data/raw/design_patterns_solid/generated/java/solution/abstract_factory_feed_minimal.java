// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=feed | tier=minimal
package org.example.patterns;

interface FeedButton { String render(); }
interface FeedDialog { String show(); }

class FeedCloudButton implements FeedButton {
    public String render() { return "cloud-btn-feed"; }
}
class FeedCloudDialog implements FeedDialog {
    public String show() { return "cloud-dlg-feed"; }
}
class FeedLocalButton implements FeedButton {
    public String render() { return "local-btn-feed"; }
}
class FeedLocalDialog implements FeedDialog {
    public String show() { return "local-dlg-feed"; }
}

interface FeedUIFactory {
    FeedButton createButton();
    FeedDialog createDialog();
}

class FeedCloudFactory implements FeedUIFactory {
    public FeedButton createButton() { return new FeedCloudButton(); }
    public FeedDialog createDialog() { return new FeedCloudDialog(); }
}

class FeedLocalFactory implements FeedUIFactory {
    public FeedButton createButton() { return new FeedLocalButton(); }
    public FeedDialog createDialog() { return new FeedLocalDialog(); }
}

public class FeedAbstractFactoryDemo {
    public static String run(FeedUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
