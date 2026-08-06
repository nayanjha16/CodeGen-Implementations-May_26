package org.example.patterns;
public class WidgetsFactoryTest {
    public static void main(String[] args) {
        WidgetsFactory f = new WidgetsFactory();
        if (!f.create("basic").operate().equals("basic-widgets")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-widgets")) throw new AssertionError();
        System.out.println("ok");
    }
}
