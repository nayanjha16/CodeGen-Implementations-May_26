package org.example.patterns;
public class CanvasBridgeTest {
    public static void main(String[] args) {
        CanvasBridge b = new CanvasAlertBridge(new CanvasFileImpl());
        String out = b.send("x");
        if (!out.equals("file:canvas:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
