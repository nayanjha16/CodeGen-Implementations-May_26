package org.example.patterns;
public class LicenseObserverTest {
    public static void main(String[] args) {
        LicenseSubject s = new LicenseSubject();
        LicenseListener l = new LicenseListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("license:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
