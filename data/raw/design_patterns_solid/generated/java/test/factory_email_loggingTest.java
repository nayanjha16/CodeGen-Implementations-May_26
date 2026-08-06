package org.example.patterns;
public class EmailFactoryTest {
    public static void main(String[] args) {
        EmailFactory f = new EmailFactory();
        if (!f.create("basic").operate().equals("basic-email")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-email")) throw new AssertionError();
        System.out.println("ok");
    }
}
