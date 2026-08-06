// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=http | tier=errors
package org.example.patterns;

interface HttpImpl {
    String write(String msg);
}

class HttpFileImpl implements HttpImpl {
    public String write(String msg) { return "file:http:" + msg; }
}

class HttpMemoryImpl implements HttpImpl {
    public String write(String msg) { return "mem:http:" + msg; }
}

public abstract class HttpBridge {
    protected final HttpImpl impl;
    protected HttpBridge(HttpImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class HttpAlertBridge extends HttpBridge {
    public HttpAlertBridge(HttpImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
