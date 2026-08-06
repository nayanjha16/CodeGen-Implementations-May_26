package org.example.patterns;
public class PluginBridgeTest {
    public static void main(String[] args) {
        PluginBridge b = new PluginAlertBridge(new PluginFileImpl());
        String out = b.send("x");
        if (!out.equals("file:plugin:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
