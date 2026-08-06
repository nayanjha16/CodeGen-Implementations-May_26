package org.example.patterns;
public class ReportChainTest {
    public static void main(String[] args) {
        ReportHandler h = new ReportLowHandler();
        h.link(new ReportHighHandler());
        if (!h.handle(2, "m").equals("high-report:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
