package org.example.patterns;
public class TodoBridgeTest {
    public static void main(String[] args) {
        TodoBridge b = new TodoAlertBridge(new TodoFileImpl());
        String out = b.send("x");
        if (!out.equals("file:todo:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
