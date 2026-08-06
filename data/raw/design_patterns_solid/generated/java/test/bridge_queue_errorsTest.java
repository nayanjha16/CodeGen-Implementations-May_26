package org.example.patterns;
public class QueueBridgeTest {
    public static void main(String[] args) {
        QueueBridge b = new QueueAlertBridge(new QueueFileImpl());
        String out = b.send("x");
        if (!out.equals("file:queue:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
