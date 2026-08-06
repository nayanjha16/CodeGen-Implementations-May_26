package org.example.patterns;
public class ReportFactoryTest {
    public static void main(String[] args) {
        ReportFactory f = new ReportFactory();
        if (!f.create("basic").operate().equals("basic-report")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-report")) throw new AssertionError();
        System.out.println("ok");
    }
}
