// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=notes | tier=errors
package org.example.patterns;

interface NotesImpl {
    String write(String msg);
}

class NotesFileImpl implements NotesImpl {
    public String write(String msg) { return "file:notes:" + msg; }
}

class NotesMemoryImpl implements NotesImpl {
    public String write(String msg) { return "mem:notes:" + msg; }
}

public abstract class NotesBridge {
    protected final NotesImpl impl;
    protected NotesBridge(NotesImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class NotesAlertBridge extends NotesBridge {
    public NotesAlertBridge(NotesImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
