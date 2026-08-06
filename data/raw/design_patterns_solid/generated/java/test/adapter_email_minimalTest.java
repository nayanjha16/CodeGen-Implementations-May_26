package org.example.patterns;
public class EmailAdapterTest {
    public static void main(String[] args) {
        EmailTarget t = new EmailAdapter(new EmailLegacyApi());
        if (!t.fetch().equals("modern-email")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
