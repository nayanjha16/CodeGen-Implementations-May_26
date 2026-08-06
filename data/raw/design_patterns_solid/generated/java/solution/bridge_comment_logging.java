// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=comment | tier=logging
package org.example.patterns;

interface CommentImpl {
    String write(String msg);
}

class CommentFileImpl implements CommentImpl {
    public String write(String msg) { return "file:comment:" + msg; }
}

class CommentMemoryImpl implements CommentImpl {
    public String write(String msg) { return "mem:comment:" + msg; }
}

public abstract class CommentBridge {
    protected final CommentImpl impl;
    protected CommentBridge(CommentImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class CommentAlertBridge extends CommentBridge {
    public CommentAlertBridge(CommentImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
