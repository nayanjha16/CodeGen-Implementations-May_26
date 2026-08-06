package org.example.patterns;
public class CommentBridgeTest {
    public static void main(String[] args) {
        CommentBridge b = new CommentAlertBridge(new CommentFileImpl());
        String out = b.send("x");
        if (!out.equals("file:comment:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
