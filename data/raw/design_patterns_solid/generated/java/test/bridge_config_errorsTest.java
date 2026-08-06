package org.example.patterns;
public class ConfigBridgeTest {
    public static void main(String[] args) {
        ConfigBridge b = new ConfigAlertBridge(new ConfigFileImpl());
        String out = b.send("x");
        if (!out.equals("file:config:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
