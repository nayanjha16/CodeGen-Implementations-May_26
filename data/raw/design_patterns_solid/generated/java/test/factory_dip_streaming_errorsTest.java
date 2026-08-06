package org.example.patterns;
public class StreamingFactoryTest {
    public static void main(String[] args) {
        StreamingFactory f = new StreamingFactory();
        if (!f.create("basic").operate().equals("basic-streaming")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-streaming")) throw new AssertionError();
        System.out.println("ok");
    }
}
