package org.example.patterns;
public class BackupTemplateTest {
    public static void main(String[] args) {
        String out = new BackupUpperTemplate().run(" ab ");
        if (!out.equals("backup|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
