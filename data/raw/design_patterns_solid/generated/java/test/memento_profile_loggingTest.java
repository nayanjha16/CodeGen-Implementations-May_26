package org.example.patterns;
public class ProfileMementoTest {
    public static void main(String[] args) {
        ProfileOriginator o = new ProfileOriginator();
        ProfileMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("profile-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
