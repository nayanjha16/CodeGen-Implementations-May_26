package org.example.patterns;
public class SensorsProxyTest {
    public static void main(String[] args) {
        if (!new SensorsProxy(true).load("1").equals("real-sensors:1")) throw new AssertionError();
        if (!new SensorsProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
