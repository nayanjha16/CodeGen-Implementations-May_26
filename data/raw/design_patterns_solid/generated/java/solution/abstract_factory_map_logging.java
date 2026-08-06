// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=map | tier=logging
package org.example.patterns;

interface MapButton { String render(); }
interface MapDialog { String show(); }

class MapCloudButton implements MapButton {
    public String render() { return "cloud-btn-map"; }
}
class MapCloudDialog implements MapDialog {
    public String show() { return "cloud-dlg-map"; }
}
class MapLocalButton implements MapButton {
    public String render() { return "local-btn-map"; }
}
class MapLocalDialog implements MapDialog {
    public String show() { return "local-dlg-map"; }
}

interface MapUIFactory {
    MapButton createButton();
    MapDialog createDialog();
}

class MapCloudFactory implements MapUIFactory {
    public MapButton createButton() { return new MapCloudButton(); }
    public MapDialog createDialog() { return new MapCloudDialog(); }
}

class MapLocalFactory implements MapUIFactory {
    public MapButton createButton() { return new MapLocalButton(); }
    public MapDialog createDialog() { return new MapLocalDialog(); }
}

public class MapAbstractFactoryDemo {
    public static String run(MapUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
