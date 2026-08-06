package org.example.patterns;
public class SessionMementoTest {
    public static void main(String[] args) {
        SessionOriginator o = new SessionOriginator();
        SessionMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("session-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
