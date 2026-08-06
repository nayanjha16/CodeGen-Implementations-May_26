package org.example.patterns;
public class SyncProxyTest {
    public static void main(String[] args) {
        if (!new SyncProxy(true).load("1").equals("real-sync:1")) throw new AssertionError();
        if (!new SyncProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
