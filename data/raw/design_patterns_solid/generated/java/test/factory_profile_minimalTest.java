package org.example.patterns;
public class ProfileFactoryTest {
    public static void main(String[] args) {
        ProfileFactory f = new ProfileFactory();
        if (!f.create("basic").operate().equals("basic-profile")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-profile")) throw new AssertionError();
        System.out.println("ok");
    }
}
