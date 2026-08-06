// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=video | tier=errors
package org.example.patterns;

interface VideoImpl {
    String write(String msg);
}

class VideoFileImpl implements VideoImpl {
    public String write(String msg) { return "file:video:" + msg; }
}

class VideoMemoryImpl implements VideoImpl {
    public String write(String msg) { return "mem:video:" + msg; }
}

public abstract class VideoBridge {
    protected final VideoImpl impl;
    protected VideoBridge(VideoImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class VideoAlertBridge extends VideoBridge {
    public VideoAlertBridge(VideoImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
