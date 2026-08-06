package org.example.patterns;
public class StreamingProxyTest {
    public static void main(String[] args) {
        if (!new StreamingProxy(true).load("1").equals("real-streaming:1")) throw new AssertionError();
        if (!new StreamingProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
