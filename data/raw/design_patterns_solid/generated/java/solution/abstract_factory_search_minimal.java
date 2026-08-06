// DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=search | tier=minimal
package org.example.patterns;

interface SearchButton { String render(); }
interface SearchDialog { String show(); }

class SearchCloudButton implements SearchButton {
    public String render() { return "cloud-btn-search"; }
}
class SearchCloudDialog implements SearchDialog {
    public String show() { return "cloud-dlg-search"; }
}
class SearchLocalButton implements SearchButton {
    public String render() { return "local-btn-search"; }
}
class SearchLocalDialog implements SearchDialog {
    public String show() { return "local-dlg-search"; }
}

interface SearchUIFactory {
    SearchButton createButton();
    SearchDialog createDialog();
}

class SearchCloudFactory implements SearchUIFactory {
    public SearchButton createButton() { return new SearchCloudButton(); }
    public SearchDialog createDialog() { return new SearchCloudDialog(); }
}

class SearchLocalFactory implements SearchUIFactory {
    public SearchButton createButton() { return new SearchLocalButton(); }
    public SearchDialog createDialog() { return new SearchLocalDialog(); }
}

public class SearchAbstractFactoryDemo {
    public static String run(SearchUIFactory factory) {
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }
}
