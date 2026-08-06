package org.example.patterns;
public class ReportMediatorTest {
    public static void main(String[] args) {
        ReportMediator m = new ReportMediator();
        new ReportColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
