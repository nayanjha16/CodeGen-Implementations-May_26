package org.example.patterns;
public class ConfigProxyTest {
    public static void main(String[] args) {
        if (!new ConfigProxy(true).load("1").equals("real-config:1")) throw new AssertionError();
        if (!new ConfigProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
