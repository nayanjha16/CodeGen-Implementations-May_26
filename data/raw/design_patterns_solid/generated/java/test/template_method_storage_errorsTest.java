package org.example.patterns;
public class StorageTemplateTest {
    public static void main(String[] args) {
        String out = new StorageUpperTemplate().run(" ab ");
        if (!out.equals("storage|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
