package org.example.patterns;
public class ReportFacadeTest {
    public static void main(String[] args) {
        ReportFacade f = new ReportFacade();
        if (!f.submit("x").equals("wrote-report:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
