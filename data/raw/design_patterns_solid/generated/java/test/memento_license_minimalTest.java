package org.example.patterns;
public class LicenseMementoTest {
    public static void main(String[] args) {
        LicenseOriginator o = new LicenseOriginator();
        LicenseMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("license-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
