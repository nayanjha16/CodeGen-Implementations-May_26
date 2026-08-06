package org.example.patterns;
public class SearchBridgeTest {
    public static void main(String[] args) {
        SearchBridge b = new SearchAlertBridge(new SearchFileImpl());
        String out = b.send("x");
        if (!out.equals("file:search:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
