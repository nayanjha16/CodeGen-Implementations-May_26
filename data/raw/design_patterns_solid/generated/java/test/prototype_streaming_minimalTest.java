package org.example.patterns;
public class StreamingPrototypeTest {
    public static void main(String[] args) {
        StreamingPrototype a = new StreamingPrototype("streaming", 2);
        StreamingPrototype b = a.copy();
        b.setLabel("streaming-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
