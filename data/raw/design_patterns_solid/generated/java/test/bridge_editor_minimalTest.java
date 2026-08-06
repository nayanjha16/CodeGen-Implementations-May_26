package org.example.patterns;
public class EditorBridgeTest {
    public static void main(String[] args) {
        EditorBridge b = new EditorAlertBridge(new EditorFileImpl());
        String out = b.send("x");
        if (!out.equals("file:editor:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
