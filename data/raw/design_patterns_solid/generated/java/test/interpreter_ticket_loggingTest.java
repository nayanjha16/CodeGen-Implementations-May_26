package org.example.patterns;
public class TicketInterpreterTest {
    public static void main(String[] args) {
        TicketInterpreter i = new TicketInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
