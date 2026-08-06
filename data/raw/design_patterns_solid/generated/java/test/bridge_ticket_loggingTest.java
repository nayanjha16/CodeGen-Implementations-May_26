package org.example.patterns;
public class TicketBridgeTest {
    public static void main(String[] args) {
        TicketBridge b = new TicketAlertBridge(new TicketFileImpl());
        String out = b.send("x");
        if (!out.equals("file:ticket:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
