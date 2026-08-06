package org.example.patterns;
public class StreamingSrpTest {
    public static void main(String[] args) {
        StreamingRecord r = new StreamingRecord("a", 3);
        if (!new StreamingFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
