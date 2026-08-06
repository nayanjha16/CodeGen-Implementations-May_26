package org.example.patterns;
public class StreamingSingletonTest {
    public static void main(String[] args) {
        StreamingSingleton a = StreamingSingleton.getInstance();
        StreamingSingleton b = StreamingSingleton.getInstance();
        a.setValue("streaming-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("streaming-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
