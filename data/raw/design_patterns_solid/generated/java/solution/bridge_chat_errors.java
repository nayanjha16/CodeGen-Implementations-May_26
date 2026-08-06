// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=chat | tier=errors
package org.example.patterns;

interface ChatImpl {
    String write(String msg);
}

class ChatFileImpl implements ChatImpl {
    public String write(String msg) { return "file:chat:" + msg; }
}

class ChatMemoryImpl implements ChatImpl {
    public String write(String msg) { return "mem:chat:" + msg; }
}

public abstract class ChatBridge {
    protected final ChatImpl impl;
    protected ChatBridge(ChatImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class ChatAlertBridge extends ChatBridge {
    public ChatAlertBridge(ChatImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
