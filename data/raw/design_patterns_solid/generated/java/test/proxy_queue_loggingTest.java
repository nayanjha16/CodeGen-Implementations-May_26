package org.example.patterns;
public class QueueProxyTest {
    public static void main(String[] args) {
        if (!new QueueProxy(true).load("1").equals("real-queue:1")) throw new AssertionError();
        if (!new QueueProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
