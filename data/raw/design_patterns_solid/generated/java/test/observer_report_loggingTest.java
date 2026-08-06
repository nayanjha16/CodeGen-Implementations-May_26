package org.example.patterns;
public class ReportObserverTest {
    public static void main(String[] args) {
        ReportSubject s = new ReportSubject();
        ReportListener l = new ReportListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("report:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
