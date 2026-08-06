package org.example.patterns;
public class GameBridgeTest {
    public static void main(String[] args) {
        GameBridge b = new GameAlertBridge(new GameFileImpl());
        String out = b.send("x");
        if (!out.equals("file:game:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
