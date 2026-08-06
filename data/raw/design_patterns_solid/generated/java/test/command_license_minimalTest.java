package org.example.patterns;
public class LicenseCommandTest {
    public static void main(String[] args) {
        LicenseCommand cmd = new LicenseActionCommand(new LicenseReceiver(), "x");
        if (!cmd.execute().equals("done-license:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
