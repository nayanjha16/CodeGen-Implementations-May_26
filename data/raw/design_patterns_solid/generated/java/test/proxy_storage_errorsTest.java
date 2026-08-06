package org.example.patterns;
public class StorageProxyTest {
    public static void main(String[] args) {
        if (!new StorageProxy(true).load("1").equals("real-storage:1")) throw new AssertionError();
        if (!new StorageProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
