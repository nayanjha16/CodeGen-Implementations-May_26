package org.example.patterns;
public class TicketObserverTest {
    public static void main(String[] args) {
        TicketSubject s = new TicketSubject();
        TicketListener l = new TicketListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("ticket:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
