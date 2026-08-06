package org.example.patterns;
public class EmailMementoTest {
    public static void main(String[] args) {
        EmailOriginator o = new EmailOriginator();
        EmailMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("email-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
