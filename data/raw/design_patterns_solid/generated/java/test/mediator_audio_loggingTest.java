package org.example.patterns;
public class AudioMediatorTest {
    public static void main(String[] args) {
        AudioMediator m = new AudioMediator();
        new AudioColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
