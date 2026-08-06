// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=video | tier=logging
package org.example.patterns;

interface VideoButton { String render(); }
interface VideoDialog { String show(); }

class VideoCloudButton implements VideoButton {
    public String render() { return "cloud-btn-video"; }
}
class VideoCloudDialog implements VideoDialog {
    public String show() { return "cloud-dlg-video"; }
}
class VideoLocalButton implements VideoButton {
    public String render() { return "local-btn-video"; }
}
class VideoLocalDialog implements VideoDialog {
    public String show() { return "local-dlg-video"; }
}

interface VideoUIFactory {
    VideoButton createButton();
    VideoDialog createDialog();
}

class VideoCloudFactory implements VideoUIFactory {
    public VideoButton createButton() { return new VideoCloudButton(); }
    public VideoDialog createDialog() { return new VideoCloudDialog(); }
}

class VideoLocalFactory implements VideoUIFactory {
    public VideoButton createButton() { return new VideoLocalButton(); }
    public VideoDialog createDialog() { return new VideoLocalDialog(); }
}

public class VideoAbstractFactoryDemo {
    public static String run(VideoUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
