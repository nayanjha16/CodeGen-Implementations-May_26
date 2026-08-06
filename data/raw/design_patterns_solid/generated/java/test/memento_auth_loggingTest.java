package org.example.patterns;
public class AuthMementoTest {
    public static void main(String[] args) {
        AuthOriginator o = new AuthOriginator();
        AuthMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("auth-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
