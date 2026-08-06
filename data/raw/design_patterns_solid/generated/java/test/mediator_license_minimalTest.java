package org.example.patterns;
public class LicenseMediatorTest {
    public static void main(String[] args) {
        LicenseMediator m = new LicenseMediator();
        new LicenseColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
