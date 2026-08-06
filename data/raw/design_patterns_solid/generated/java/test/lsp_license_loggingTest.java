package org.example.patterns;
public class LicenseLspTest {
    public static void main(String[] args) {
        LicenseShape[] arr = new LicenseShape[] { new LicenseRectangle(2,3), new LicenseSquare(4) };
        if (LicenseLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
