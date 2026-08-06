package org.example.patterns;
public class StreamingMediatorTest {
    public static void main(String[] args) {
        StreamingMediator m = new StreamingMediator();
        new StreamingColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
