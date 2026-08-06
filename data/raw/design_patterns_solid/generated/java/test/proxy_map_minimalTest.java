package org.example.patterns;
public class MapProxyTest {
    public static void main(String[] args) {
        if (!new MapProxy(true).load("1").equals("real-map:1")) throw new AssertionError();
        if (!new MapProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
