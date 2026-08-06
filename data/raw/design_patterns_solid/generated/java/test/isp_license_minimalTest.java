package org.example.patterns;
public class LicenseIspTest {
    public static void main(String[] args) {
        LicenseStore st = new LicenseStore();
        st.write("x");
        if (!LicenseIspClient.mirror(st).equals("license:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
