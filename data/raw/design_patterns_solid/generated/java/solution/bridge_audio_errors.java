// DesignPatternsSolid | kind=design_pattern | label=bridge | domain=audio | tier=errors
package org.example.patterns;

interface AudioImpl {
    String write(String msg);
}

class AudioFileImpl implements AudioImpl {
    public String write(String msg) { return "file:audio:" + msg; }
}

class AudioMemoryImpl implements AudioImpl {
    public String write(String msg) { return "mem:audio:" + msg; }
}

public abstract class AudioBridge {
    protected final AudioImpl impl;
    protected AudioBridge(AudioImpl impl) { this.impl = impl; }
    public abstract String send(String msg);
}

class AudioAlertBridge extends AudioBridge {
    public AudioAlertBridge(AudioImpl impl) { super(impl); }
    public String send(String msg) { return impl.write("ALERT-" + msg); }
}
