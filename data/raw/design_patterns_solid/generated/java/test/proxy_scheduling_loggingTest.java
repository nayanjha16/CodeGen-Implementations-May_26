package org.example.patterns;
public class SchedulingProxyTest {
    public static void main(String[] args) {
        if (!new SchedulingProxy(true).load("1").equals("real-scheduling:1")) throw new AssertionError();
        if (!new SchedulingProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
