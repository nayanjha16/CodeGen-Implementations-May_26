package org.example.patterns;
public class SmsMediatorTest {
    public static void main(String[] args) {
        SmsMediator m = new SmsMediator();
        new SmsColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
