package org.example.patterns;
public class HttpBridgeTest {
    public static void main(String[] args) {
        HttpBridge b = new HttpAlertBridge(new HttpFileImpl());
        String out = b.send("x");
        if (!out.equals("file:http:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
