// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=search | tier=errors
package org.example.patterns;

interface SearchImpl {
    String write(String msg);
}

class SearchFileImpl implements SearchImpl {
    public String write(String msg) { return "file:search:" + msg; }
}

class SearchMemoryImpl implements SearchImpl {
    public String write(String msg) { return "mem:search:" + msg; }
}

public abstract class SearchBridge {
    protected final SearchImpl impl;
    protected SearchBridge(SearchImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class SearchAlertBridge extends SearchBridge {
    public SearchAlertBridge(SearchImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
