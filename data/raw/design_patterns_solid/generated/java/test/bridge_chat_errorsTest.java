package org.example.patterns;
public class ChatBridgeTest {
    public static void main(String[] args) {
        ChatBridge b = new ChatAlertBridge(new ChatFileImpl());
        String out = b.send("x");
        if (!out.equals("file:chat:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
