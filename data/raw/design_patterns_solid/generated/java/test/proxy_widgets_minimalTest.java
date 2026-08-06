package org.example.patterns;
public class WidgetsProxyTest {
    public static void main(String[] args) {
        if (!new WidgetsProxy(true).load("1").equals("real-widgets:1")) throw new AssertionError();
        if (!new WidgetsProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
