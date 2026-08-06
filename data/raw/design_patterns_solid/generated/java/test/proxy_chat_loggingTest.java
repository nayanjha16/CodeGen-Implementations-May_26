package org.example.patterns;
public class ChatProxyTest {
    public static void main(String[] args) {
        if (!new ChatProxy(true).load("1").equals("real-chat:1")) throw new AssertionError();
        if (!new ChatProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
