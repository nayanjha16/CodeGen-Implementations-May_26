package org.example.patterns;
public class QueueMediatorTest {
    public static void main(String[] args) {
        QueueMediator m = new QueueMediator();
        new QueueColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
