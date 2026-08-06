package org.example.patterns;
public class LicenseAdapterTest {
    public static void main(String[] args) {
        LicenseTarget t = new LicenseAdapter(new LicenseLegacyApi());
        if (!t.fetch().equals("modern-license")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
