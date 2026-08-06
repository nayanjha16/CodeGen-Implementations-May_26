package org.example.patterns;
public class TaxFactoryTest {
    public static void main(String[] args) {
        TaxFactory f = new TaxFactory();
        if (!f.create("basic").operate().equals("basic-tax")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-tax")) throw new AssertionError();
        System.out.println("ok");
    }
}
