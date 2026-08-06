package org.example.patterns;
public class EmailMediatorTest {
    public static void main(String[] args) {
        EmailMediator m = new EmailMediator();
        new EmailColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
