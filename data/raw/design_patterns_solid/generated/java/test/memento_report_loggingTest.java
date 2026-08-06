package org.example.patterns;
public class ReportMementoTest {
    public static void main(String[] args) {
        ReportOriginator o = new ReportOriginator();
        ReportMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("report-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
