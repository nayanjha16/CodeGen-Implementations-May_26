package org.example.patterns;
public class SyncMediatorTest {
    public static void main(String[] args) {
        SyncMediator m = new SyncMediator();
        new SyncColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
