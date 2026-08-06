package org.example.patterns;
public class HttpMediatorTest {
    public static void main(String[] args) {
        HttpMediator m = new HttpMediator();
        new HttpColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
