package org.example.patterns;
public class ReportProxyTest {
    public static void main(String[] args) {
        if (!new ReportProxy(true).load("1").equals("real-report:1")) throw new AssertionError();
        if (!new ReportProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
