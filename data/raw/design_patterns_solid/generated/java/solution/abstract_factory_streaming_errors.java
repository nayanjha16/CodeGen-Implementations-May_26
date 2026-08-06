// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=streaming | tier=errors
package org.example.patterns;

interface StreamingButton { String render(); }
interface StreamingDialog { String show(); }

class StreamingCloudButton implements StreamingButton {
    public String render() { return "cloud-btn-streaming"; }
}
class StreamingCloudDialog implements StreamingDialog {
    public String show() { return "cloud-dlg-streaming"; }
}
class StreamingLocalButton implements StreamingButton {
    public String render() { return "local-btn-streaming"; }
}
class StreamingLocalDialog implements StreamingDialog {
    public String show() { return "local-dlg-streaming"; }
}

interface StreamingUIFactory {
    StreamingButton createButton();
    StreamingDialog createDialog();
}

class StreamingCloudFactory implements StreamingUIFactory {
    public StreamingButton createButton() { return new StreamingCloudButton(); }
    public StreamingDialog createDialog() { return new StreamingCloudDialog(); }
}

class StreamingLocalFactory implements StreamingUIFactory {
    public StreamingButton createButton() { return new StreamingLocalButton(); }
    public StreamingDialog createDialog() { return new StreamingLocalDialog(); }
}

public class StreamingAbstractFactoryDemo {
    public static String run(StreamingUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
