package org.example.patterns;
public class ProfileTemplateTest {
    public static void main(String[] args) {
        String out = new ProfileUpperTemplate().run(" ab ");
        if (!out.equals("profile|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
