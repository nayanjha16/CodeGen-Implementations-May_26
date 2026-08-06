package org.example.patterns;
public class EmailSingletonTest {
    public static void main(String[] args) {
        EmailSingleton a = EmailSingleton.getInstance();
        EmailSingleton b = EmailSingleton.getInstance();
        a.setValue("email-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("email-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
